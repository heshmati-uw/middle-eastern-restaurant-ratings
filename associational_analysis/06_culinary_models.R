args <- commandArgs(FALSE);root <- dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])))
out <- file.path(root,'outputs')
d <- read.csv(file.path(root,'private','culinary_supported.csv'),colClasses=c(county_fips='character'))
d$hist <- log1p(d$prior_reviews)
d$price <- factor(ifelse(grepl('^\\${1,4}$',d$price),d$price,'Missing'))
features <- grep('^(dish_|countrydish_|tradition_)',names(d),value=TRUE)
# Use all measured binary food features. QR removes exact redundancies, not insignificant terms.
fit <- function(vars,s=d) {
 X <- model.matrix(reformulate(vars),s)[,-1,drop=FALSE]
 x <- apply(X,2,function(z)z-ave(z,s$county_fips));y <- s$rating-ave(s$rating,s$county_fips)
 q <- qr(x,tol=1e-8);keep <- sort(q$pivot[seq_len(q$rank)]);dropped <- setdiff(colnames(x),colnames(x)[keep]);x<-x[,keep,drop=FALSE]
 stopifnot('med'%in%colnames(x));B<-solve(crossprod(x));b<-drop(B%*%crossprod(x,y));names(b)<-colnames(x)
 u<-y-drop(x%*%b);S<-rowsum(x*u,s$county_fips);G<-nrow(S);N<-nrow(s);K<-ncol(x)+G
 stopifnot(N>K,G>2,max(abs(crossprod(x,u)))<1e-6)
 V<-B%*%crossprod(S)%*%B*G/(G-1)*(N-1)/(N-K);se<-sqrt(V['med','med']);e<-b['med']
 list(result=data.frame(estimate=e,se=se,lo=e-qt(.975,G-1)*se,hi=e+qt(.975,G-1)*se,p=2*pt(-abs(e/se),G-1),restaurants=N,ME=sum(s$med==0),Mediterranean=sum(s$med==1),counties=G,regressors=ncol(x)),dropped=dropped,b=b,V=V)
}
specs<-list('County FE only'='med','Add prior review volume'=c('med','hist'),'Add culinary profiles'=c('med','hist',features),'Add snapshot price'=c('med','hist',features,'price'))
results<-list();audit<-list()
for(n in names(specs)) {m<-fit(specs[[n]]);results[[n]]<-cbind(model=n,m$result);audit[[n]]<-m$dropped}
r<-do.call(rbind,results);rownames(r)<-NULL
write.csv(r,file.path(out,'culinary_positioning_results.csv'),row.names=FALSE)
writeLines(capture.output(audit),file.path(out,'culinary_redundant_features.txt'))
# Independent explicit-dummy check of the baseline clustered covariance.
base<-fit(c('med','hist'));explicit<-lm(rating~med+hist+factor(county_fips),d)
X<-model.matrix(explicit);B<-solve(crossprod(X));S<-rowsum(X*residuals(explicit),d$county_fips);G<-nrow(S);N<-nrow(d);K<-ncol(X)
V<-B%*%crossprod(S)%*%B*G/(G-1)*(N-1)/(N-K)
stopifnot(max(abs(base$b-coef(explicit)[names(base$b)]))<1e-8,max(abs(base$V-V[names(base$b),names(base$b)]))<1e-8)
writeLines('County-absorbed baseline coefficients and clustered covariance match explicit dummy OLS to 1e-8. All nested models use the same restaurant sample.',file.path(out,'culinary_validation.txt'))
pf<-function(p)ifelse(p<.001,'p < .001',sprintf('p = %.3f',p))
draw<-function(){
 par(mar=c(5,13,5,3),oma=c(5,0,0,0),family='sans')
 yy<-4:1;xr<-range(c(0,r$lo,r$hi));span<-diff(xr)
 plot(xr+c(-.1,.65)*span,c(.5,4.6),type='n',axes=FALSE,xlab='Mediterranean minus visibly ME rating (stars)',ylab='')
 axis(1);axis(2,at=yy,labels=r$model,las=1,cex.axis=.9);abline(v=0,lty=2,col='gray50')
 segments(r$lo,yy,r$hi,yy,lwd=3,col='#087E8B');points(r$estimate,yy,pch=16,col='#087E8B',cex=1.2)
 text(max(r$hi)+.08*span,yy,sprintf('%+.3f stars; %s',r$estimate,pf(r$p)),adj=0,cex=.9)
 title('Does Mediterranean positioning predict different ratings?',line=3)
 mtext(sprintf('Comparable pre-election food evidence | Mediterranean n = %s; visibly ME n = %s | %s counties',r$Mediterranean[1],r$ME[1],r$counties[1]),3,line=1,cex=.85)
 mtext('Nov 14, 2016-Apr 9, 2017. Equal restaurant weights; county fixed effects throughout.',1,outer=TRUE,line=1,cex=.85)
 mtext('95% county-clustered intervals. P-values test a zero positioning coefficient; nested sensitivity models.',1,outer=TRUE,line=2.3,cex=.8)
 mtext('Same-county culinary peer required; no one-to-one matching. Food mentions proxy offerings, not identical menus.',1,outer=TRUE,line=3.6,cex=.8)
}
png(file.path(out,'culinary_positioning.png'),width=1800,height=1000,res=150);draw();dev.off()
pdf(file.path(out,'culinary_positioning.pdf'),width=12,height=1000/150);draw();dev.off()
print(r,digits=5,row.names=FALSE)
