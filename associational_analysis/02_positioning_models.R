args <- commandArgs(trailingOnly=FALSE)
script <- sub('^--file=','',args[grepl('^--file=',args)])
root <- dirname(normalizePath(script));out <- file.path(root,'outputs')
d <- read.csv(file.path(root,'private','restaurant_levels.csv'),colClasses=c(county_fips='character'))
stopifnot(!anyDuplicated(d$gmap_id),all(d$rating>=1 & d$rating<=5),all(d$prior_reviews>=0),all(d$gop_share>=0 & d$gop_share<=1))
d$hist <- log1p(d$prior_reviews);d$vote10 <- (d$gop_share-.5)*10
d$position <- factor(d$label,levels=c('American','National','Middle Eastern','Mediterranean'))
d$price <- factor(d$price)
support <- aggregate(gmap_id~label+county_fips,d,length);names(support)[3] <- 'restaurants'
write.csv(support,file.path(out,'county_label_support.csv'),row.names=FALSE)
counts <- aggregate(cbind(outcome_reviews,prior_reviews)~label,d,sum)
counts$restaurants <- as.integer(table(d$position)[match(counts$label,levels(d$position))])
counts$mean_rating <- sapply(counts$label,function(g)mean(d$rating[d$label==g]))
write.csv(counts,file.path(out,'sample_counts.csv'),row.names=FALSE)
keep_counties <- names(which(tapply(d$label,d$county_fips,function(x)length(unique(x)))>=2))
s <- d[d$county_fips %in% keep_counties,]
fit <- function(rhs,s) {
 X <- model.matrix(rhs,s);X <- X[,colnames(X)!='(Intercept)',drop=FALSE]
 within <- function(x)x-ave(x,s$county_fips)
 x <- apply(X,2,within);y <- within(s$rating)
 stopifnot(qr(x)$rank==ncol(x))
 B <- solve(crossprod(x));b <- drop(B%*%crossprod(x,y));names(b)<-colnames(x)
 u <- y-drop(x%*%b);S <- rowsum(x*u,s$county_fips);G <- nrow(S);N <- nrow(s);K <- ncol(x)+G
 V <- B%*%crossprod(S)%*%B*G/(G-1)*(N-1)/(N-K)
 # Meaningful verification: absorbed fit agrees with within-county normal equations.
 stopifnot(max(abs(crossprod(x,u)))<1e-6)
 list(b=b,V=V,df=G-1,N=N,G=G,rows=s,X=X)
}
linear <- function(m,w) {
 e <- sum(w*m$b);se <- sqrt(drop(t(w)%*%m$V%*%w))
 data.frame(estimate=e,se,lo=e-qt(.975,m$df)*se,hi=e+qt(.975,m$df)*se,p=2*pt(-abs(e/se),m$df),restaurants=m$N,counties=m$G)
}
models <- list('County FE'=~position,'Prior volume'=~position+hist,'Price sensitivity'=~position+hist+price)
res <- list();grad <- list();fits <- list()
for(name in names(models)) {
 m <- fit(models[[name]],s);fits[[name]]<-m
 for(pair in combn(levels(s$position),2,simplify=FALSE)) {
  w <- setNames(rep(0,length(m$b)),names(m$b))
  for(j in 1:2)if(pair[j]!='American')w[paste0('position',pair[j])]<-c(-1,1)[j]
  res[[length(res)+1]] <- cbind(data.frame(model=name,contrast=paste(pair[2],'minus',pair[1])),linear(m,w))
 }
}
# Initial political-moderation specification; price stays a sensitivity control.
s$nv <- as.integer(s$label=='National')*s$vote10
s$mev <- as.integer(s$label=='Middle Eastern')*s$vote10
s$medv <- as.integer(s$label=='Mediterranean')*s$vote10
m <- fit(~position+hist+nv+mev+medv,s)
term <- c(National='nv','Middle Eastern'='mev',Mediterranean='medv')
for(pair in combn(levels(s$position),2,simplify=FALSE)) {
 w <- setNames(rep(0,length(m$b)),names(m$b))
 for(j in 1:2)if(pair[j]!='American')w[term[pair[j]]]<-c(-1,1)[j]
 grad[[length(grad)+1]] <- cbind(data.frame(model='County FE + prior volume',contrast=paste(pair[2],'minus',pair[1])),linear(m,w))
}
r <- do.call(rbind,res);g <- do.call(rbind,grad)
r$p_holm <- ave(r$p,r$model,FUN=function(p)p.adjust(p,'holm'));g$p_holm <- p.adjust(g$p,'holm')
# Independent verification against explicit county dummy OLS on a manageable subset.
test_counties <- head(names(which(tapply(s$label,s$county_fips,function(x)length(unique(x)))==4)),20)
test <- s[s$county_fips %in% test_counties,]
stopifnot(length(test_counties)>=3)
small <- fit(~position+hist,test)
explicit <- lm(rating~position+hist+factor(county_fips),test)
X <- model.matrix(explicit);B <- solve(crossprod(X));S <- rowsum(X*residuals(explicit),test$county_fips)
G <- nrow(S);N <- nrow(test);K <- ncol(X)
V <- B%*%crossprod(S)%*%B*G/(G-1)*(N-1)/(N-K)
stopifnot(max(abs(small$b-coef(explicit)[names(small$b)]))<1e-8)
stopifnot(max(abs(small$V-V[names(small$b),names(small$b)]))<1e-8)
write.csv(r,file.path(out,'positioning_contrasts.csv'),row.names=FALSE)
write.csv(g,file.path(out,'political_gradients.csv'),row.names=FALSE)
writeLines(capture.output(sessionInfo()),file.path(out,'R_session.txt'))
writeLines(c(paste('Raw outcome sample:',nrow(d),'restaurants'),paste('County-FE support:',nrow(s),'restaurants in',length(unique(s$county_fips)),'counties'),paste('Price missing:',sum(d$price=='Missing')),'Absorbed coefficients and clustered covariance agree with explicit dummy OLS on 20 counties to 1e-8.'),file.path(out,'validation.txt'))
draw <- function() {
 par(mfrow=c(1,2),mar=c(5,11,3,1),oma=c(2,0,2,0),family='sans')
 for(kind in c('level','gradient')) {
  z <- if(kind=='level')subset(r,model=='Prior volume') else g
  z <- z[nrow(z):1,];yy <- seq_len(nrow(z))
  plot(range(c(z$lo,z$hi,0)),range(yy)+c(-.5,.5),type='n',axes=FALSE,ylab='',xlab=if(kind=='level')'Adjusted rating difference (stars)' else 'Difference per 10 vote-share points')
  axis(1);axis(2,at=yy,labels=gsub('Middle Eastern','literal ME',z$contrast),las=1,cex.axis=.8);abline(v=0,lty=2,col='gray50')
  segments(z$lo,yy,z$hi,yy,col='#007D91',lwd=2);points(z$estimate,yy,pch=16,col='#007D91')
  title(if(kind=='level')'Positioning associations' else 'Political moderation')
 }
 mtext('Raw-data first pass: November 14, 2016-April 9, 2017',3,outer=TRUE,line=.5,font=2)
 mtext('Equal restaurant weights; county fixed effects; log prior review count. 95% county-clustered intervals. Observational associations.',1,outer=TRUE,line=.5,cex=.8)
}
png(file.path(out,'first_pass.png'),width=1900,height=850,res=150);draw();dev.off()
pdf(file.path(out,'first_pass.pdf'),width=1900/150,height=850/150);draw();dev.off()
print(counts,row.names=FALSE);print(subset(r,model=='Prior volume'),digits=3,row.names=FALSE);print(g,digits=3,row.names=FALSE)
