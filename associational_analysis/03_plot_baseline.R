args <- commandArgs(trailingOnly=FALSE);root <- dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])))
out <- file.path(root,'outputs')
r <- subset(read.csv(file.path(out,'positioning_contrasts.csv')),model=='Prior volume')
g <- read.csv(file.path(out,'political_gradients.csv'))
s <- read.csv(file.path(out,'county_label_support.csv'),colClasses=c(county_fips='character'))
keep <- names(which(table(s$county_fips)>=2));s <- s[s$county_fips %in% keep,]
n <- aggregate(restaurants~label,s,sum);stopifnot(sum(n$restaurants)==unique(r$restaurants))
write.csv(n,file.path(out,'baseline_estimation_counts.csv'),row.names=FALSE)
fmt <- function(p)ifelse(p<.001,'<.001',sprintf('%.3f',p))
draw <- function() {
 par(mfrow=c(2,1),mar=c(4.2,14.5,3.3,13),oma=c(3.8,0,4.7,0),family='sans')
 for(k in 1:2) {
  z <- if(k==1)r else g;yy <- 6:1
  xr <- if(k==1)c(-.10,.29) else c(-.065,.08)
  plot(xr,c(.5,6.8),type='n',axes=FALSE,xlab=if(k==1)'Adjusted rating difference (stars)' else 'Change in rating difference per 10 percentage points of Trump vote',ylab='')
  axis(1,cex.axis=.9);axis(2,at=yy,labels=gsub('Middle Eastern','literal ME',z$contrast),las=1,tick=FALSE,cex.axis=.92)
  abline(v=0,lty=2,col='gray50');abline(h=yy,col='gray92')
  segments(z$lo,yy,z$hi,yy,col='#007D91',lwd=2);points(z$estimate,yy,pch=16,col='#007D91',cex=1)
  title(if(k==1)'A. Positioning and rating levels' else 'B. Positioning differences across political environments',adj=0,line=1.5)
  u <- par('usr');dx <- diff(u[1:2]);par(xpd=NA)
  xx <- u[2]+dx*c(.045,.14,.235)
  text(xx,6.7,c('Estimate','p','Holm p'),font=2,cex=.9)
  text(xx[1],yy,sprintf('%+.3f',z$estimate),cex=.9)
  text(xx[2],yy,fmt(z$p),cex=.9);text(xx[3],yy,fmt(z$p_holm),cex=.9)
  par(xpd=FALSE)
 }
 mtext('Baseline associations before culinary controls',3,outer=TRUE,line=3,font=2,cex=1.35)
 mtext('November 14, 2016-April 9, 2017 | 24,706 restaurants in 526 counties | One observation per restaurant',3,outer=TRUE,line=1.6,cex=1)
 counts <- setNames(n$restaurants,n$label)
 mtext(sprintf('Estimation counts: American %s  |  National %s  |  Literal Middle Eastern %s  |  Mediterranean %s',format(counts['American'],big.mark=','),format(counts['National'],big.mark=','),format(counts['Middle Eastern'],big.mark=','),format(counts['Mediterranean'],big.mark=',')),3,outer=TRUE,line=.3,cex=.96)
 mtext('Both models include county fixed effects and log(1 + reviews before November 8, 2016). Equal restaurant weights; no matching.',1,outer=TRUE,line=.3,cex=.86)
 mtext('Bars: 95% county-clustered confidence intervals. Holm adjustment covers six contrasts separately within each panel.',1,outer=TRUE,line=1.5,cex=.86)
 mtext('National pools eight national primary labels. Literal ME is the Middle Eastern primary label alone. No culinary or price controls in these panels.',1,outer=TRUE,line=2.7,cex=.86)
}
png(file.path(out,'baseline_with_pvalues.png'),width=2100,height=1450,res=150);draw();dev.off()
pdf(file.path(out,'baseline_with_pvalues.pdf'),width=14,height=1450/150);draw();dev.off()
print(n,row.names=FALSE)

