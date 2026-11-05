args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])))
out<-file.path(root,'outputs')
d<-read.csv(file.path(root,'private','culinary_supported.csv'),colClasses=c(county_fips='character'))
stopifnot(nrow(d)==487,!anyDuplicated(d$gmap_id))
d$hist<-log1p(d$prior_reviews);d$trump<-as.integer(d$gop_share>.5);d$med_trump<-d$med*d$trump
features<-grep('^(dish_|countrydish_|tradition_)',names(d),value=TRUE)
X<-model.matrix(reformulate(c('med','med_trump','hist',features)),d)[,-1,drop=FALSE]
x<-apply(X,2,function(z)z-ave(z,d$county_fips));y<-d$rating-ave(d$rating,d$county_fips)
q<-qr(x,tol=1e-8);keep<-sort(q$pivot[seq_len(q$rank)]);x<-x[,keep,drop=FALSE]
stopifnot(all(c('med','med_trump')%in%colnames(x)))
B<-solve(crossprod(x));b<-drop(B%*%crossprod(x,y));names(b)<-colnames(x)
u<-y-drop(x%*%b);S<-rowsum(x*u,d$county_fips);G<-nrow(S);N<-nrow(d);K<-ncol(x)+G
V<-B%*%crossprod(S)%*%B*G/(G-1)*(N-1)/(N-K)
counts<-do.call(rbind,lapply(0:1,function(t){s<-d[d$trump==t,];data.frame(group=if(t)'Trump-majority' else 'Other counties',restaurants=nrow(s),Mediterranean=sum(s$med==1),ME=sum(s$med==0),counties=length(unique(s$county_fips)),reviews=sum(s$outcome_reviews))}))
contrast<-function(name,w,df){e<-sum(w*b);se<-sqrt(drop(t(w)%*%V%*%w));data.frame(contrast=name,estimate=e,se=se,lo=e-qt(.975,df)*se,hi=e+qt(.975,df)*se,p=2*pt(-abs(e/se),df),df=df,p_conventional=2*pt(-abs(e/se),G-1))}
w<-setNames(rep(0,length(b)),names(b));w['med']<-1
other<-contrast('Other counties',w,counts$counties[1]-1)
w['med_trump']<-1;trump<-contrast('Trump-majority',w,counts$counties[2]-1)
w['med']<-0;difference<-contrast('Trump-majority minus other association',w,min(counts$counties)-1)
r<-rbind(other,trump,difference)
write.csv(r,file.path(out,'culinary_vote_results.csv'),row.names=FALSE)
write.csv(counts,file.path(out,'culinary_vote_counts.csv'),row.names=FALSE)
# Explicit-dummy validation on the exact selected full-rank design.
raw<-X[,colnames(x),drop=FALSE];Z<-cbind(model.matrix(~0+factor(county_fips),d),raw)
be<-solve(crossprod(Z),crossprod(Z,d$rating));ue<-drop(d$rating-Z%*%be)
BZ<-solve(crossprod(Z));SZ<-rowsum(Z*ue,d$county_fips);VZ<-BZ%*%crossprod(SZ)%*%BZ*G/(G-1)*(N-1)/(N-ncol(Z))
stopifnot(max(abs(b-be[names(b),1]))<1e-8,max(abs(V-VZ[names(b),names(b)]))<1e-8)
writeLines(c('Same 487 restaurants as pooled culinary analysis; shared culinary and history slopes; county FE; med x Trump majority interaction.',
 'CR1 covariance clustered by county. Displayed t df: other 49, Trump 6, difference 6 (smaller group county count minus one). Conventional df56 p-values also exported.',
 'This conservative df choice is not an exact small-sample correction; seven Trump-majority counties limit inference.',
 'Full food-adjusted absorbed coefficients and covariance match explicit county-dummy OLS to 1e-8.'),file.path(out,'culinary_vote_validation.txt'))
pf<-function(p)ifelse(p<.001,'p < .001',sprintf('p = %.3f',p))
draw<-function(){par(mar=c(5,12,5,2),oma=c(5,0,0,0),family='sans');z<-r[1:2,];yy<-2:1;xr<-range(c(0,z$lo,z$hi));span<-diff(xr)
 plot(xr+c(-.05,.7)*span,c(.5,2.55),type='n',axes=FALSE,xlab='Adjusted Mediterranean minus visibly ME rating (stars)',ylab='')
 axis(1);axis(2,at=yy,labels=z$contrast,las=1);abline(v=0,lty=2,col='gray50')
 cols<-c('#087E8B','#B96326');segments(z$lo,yy,z$hi,yy,lwd=3,col=cols);points(z$estimate,yy,pch=16,col=cols,cex=1.3)
 for(i in 1:2){text(max(z$hi)+.06*span,yy[i]+.09,sprintf('%+.3f stars; %s',z$estimate[i],pf(z$p[i])),adj=0);text(max(z$hi)+.06*span,yy[i]-.12,sprintf('Med n = %s; ME n = %s\n%s restaurants; %s counties',counts$Mediterranean[i],counts$ME[i],counts$restaurants[i],counts$counties[i]),adj=0,cex=.85)}
 title('Culinary-adjusted positioning associations by county vote',line=3)
 mtext(sprintf('Difference between associations: %+.3f stars; %s',difference$estimate,pf(difference$p)),3,line=1,cex=1)
 mtext('Same 487 restaurants; Nov 14, 2016-Apr 9, 2017; equal restaurant weights.',1,outer=TRUE,line=1,cex=.85)
 mtext('County FE + historical review volume + culinary profiles; common control slopes, label x county-vote interaction.',1,outer=TRUE,line=2.2,cex=.8)
 mtext('95% county-clustered intervals. Conservative t df: other 49; Trump and difference 6. Only 7 Trump-majority counties.',1,outer=TRUE,line=3.4,cex=.8)
}
png(file.path(out,'culinary_vote.png'),width=1800,height=950,res=150);draw();dev.off()
pdf(file.path(out,'culinary_vote.pdf'),width=12,height=950/150);draw();dev.off()
print(counts,row.names=FALSE);print(r,row.names=FALSE,digits=5)
