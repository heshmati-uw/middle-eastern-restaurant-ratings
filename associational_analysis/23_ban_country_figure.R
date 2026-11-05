args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'ban_country_monthly.csv'));d$date<-as.Date(paste0(d$month,'-15'))
draw<-function(){
 groups<-c('Ban-country associated ME','Other literal ME','WPME','Medit');cols<-c('#B75A2A','#B28A66','#007F86','#6B52A3')
 par(mar=c(4,5,4,1),oma=c(12.5,0,1,0),family='sans')
 plot(range(as.Date(c('2015-12-01','2017-04-30'))),c(0,78),type='n',axes=FALSE,xlab='',ylab='Restaurants with at least one review')
 axis(2,at=seq(0,70,10),las=1);axis.Date(1,at=sort(unique(d$date)),format='%b\n%Y',cex.axis=.8);abline(h=seq(0,70,10),col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray35');abline(v=as.Date('2017-01-27'),lty=2,col='gray35')
 for(i in 1:4){z<-d[d$group==groups[i],];lines(z$date,z$restaurants,col=cols[i],lwd=2,pch=15+i,type='o',cex=.7)}
 for(day in sort(unique(d$date))){z<-d[d$date==day,];vals<-z$restaurants[match(groups,z$group)];ly<-vals+1.8;ord<-order(vals)
  ly[ord[1]]<-vals[ord[1]]-1.7
  for(j in 2:4)ly[ord[j]]<-max(ly[ord[j]],ly[ord[j-1]]+2.6)
  for(i in 1:4)text(day,ly[i],labels=vals[i],col=cols[i],cex=.75,xpd=TRUE)
 }
 legend('topleft',legend=c('Ban-country associated ME','Other ME','WPME','Medit'),col=cols,pch=16:19,lty=1,bty='n',cex=.95)
 title('Association with the seven countries affected by the first travel ban',line=2,cex.main=1.15)
 mtext('Same seven Trump-majority counties | December 2015-April 2017 | Seven-country food lists',3,line=.5,cex=.9)
 mtext('SEVEN-COUNTRY DEFINITION: Iran, Iraq, Syria, Yemen, Libya, Somalia and Sudan',1,outer=TRUE,line=.5,adj=0,at=.065,cex=.9,font=2)
 mtext('ME: Persian, Syrian or Yemenite tag OR a Middle Eastern tag + at least one ban-country-listed food mention.',1,outer=TRUE,line=1.8,adj=0,at=.065,cex=.87,col=cols[1])
 mtext('Other ME: all remaining Middle Eastern-primary-tagged restaurants not already counted in ME.',1,outer=TRUE,line=3,adj=0,at=.065,cex=.87,col='#856344')
 mtext('WPME: a Mediterranean tag + at least one ban-country-listed food mention; the same food rule as literal ME.',1,outer=TRUE,line=4.2,adj=0,at=.065,cex=.87,col=cols[3])
 mtext('Medit: ALL remaining Mediterranean-tagged restaurants not classified as WPME; no additional food requirement.',1,outer=TRUE,line=5.4,adj=0,at=.065,cex=.87,col=cols[4])
 mtext('Non-ban national primary tags are excluded. A literal Middle Eastern primary tag remains eligible through food evidence.',1,outer=TRUE,line=6.8,adj=0,at=.065,cex=.8)
 mtext('Any-date food evidence, including after April 2017. Shared dishes count if linked to at least one of the seven countries.',1,outer=TRUE,line=7.9,adj=0,at=.065,cex=.8)
 mtext('Monthly counts include all restaurants reviewed that month; no matching or balanced review cohort. American restaurants excluded.',1,outer=TRUE,line=9,adj=0,at=.065,cex=.8)
 mtext('Jan 24 coverage (dotted); Jan 27 implementation (dashed). Counts describe review activity, not openings or closures.',1,outer=TRUE,line=10.1,adj=0,at=.065,cex=.8)
}
png(file.path(out,'ban_country_monthly.png'),width=1900,height=1600,res=150);draw();dev.off()
pdf(file.path(out,'ban_country_monthly.pdf'),width=1900/150,height=1600/150);draw();dev.off()
