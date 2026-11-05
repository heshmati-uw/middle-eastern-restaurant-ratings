args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'national_association_monthly.csv'));d$date<-as.Date(paste0(d$month,'-15'))
draw<-function(){
 groups<-c('Nationally associated ME','Other literal ME','WPME','All other Mediterranean');cols<-c('#B75A2A','#B28A66','#007F86','#6B52A3')
 par(mar=c(4,5,4,1),oma=c(5,0,1,0),family='sans')
 plot(range(as.Date(c('2015-12-01','2017-04-30'))),c(0,78),type='n',axes=FALSE,xlab='',ylab='Restaurants with at least one review')
 axis(2,at=seq(0,70,10),las=1);axis.Date(1,at=sort(unique(d$date)),format='%b\n%Y',cex.axis=.8);abline(h=seq(0,70,10),col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray35');abline(v=as.Date('2017-01-27'),lty=2,col='gray35')
 for(i in 1:4){z<-d[d$group==groups[i],];lines(z$date,z$restaurants,col=cols[i],lwd=2,pch=15+i,type='o',cex=.7)}
 for(day in sort(unique(d$date))){z<-d[d$date==day,];vals<-z$restaurants[match(groups,z$group)];ly<-vals+1.8;ord<-order(vals)
  ly[ord[1]]<-vals[ord[1]]-1.7
  for(j in 2:4)ly[ord[j]]<-max(ly[ord[j]],ly[ord[j-1]]+2.6)
  for(i in 1:4)text(day,ly[i],labels=vals[i],col=cols[i],cex=.75,xpd=TRUE)
 }
 legend('topleft',legend=c('Nationally associated ME: national tag OR literal ME + country-listed food','Other literal ME: no qualifying country-listed food mention','WPME: Mediterranean label + country-listed food','All other Mediterranean restaurants'),col=cols,pch=16:19,lty=1,bty='n',cex=.85)
 title('National association from positioning labels or food evidence',line=2,cex.main=1.15)
 mtext('Seven Trump-majority counties | December 2015-April 2017 | 12-country registry',3,line=.5,cex=.9)
 mtext('All restaurants reviewed in each month; no matching or balanced review cohort. American restaurants excluded.',1,outer=TRUE,line=.4,cex=.85)
 mtext('Food evidence uses any available review date and can postdate April 2017; it does not establish historical menus or nationality.',1,outer=TRUE,line=1.6,cex=.85)
 mtext('Literal ME and Mediterranean use the SAME country-listed food rule. National tags qualify directly; shared dishes count.',1,outer=TRUE,line=2.8,cex=.85)
 mtext('Jan 24 coverage (dotted); Jan 27 implementation (dashed). Counts measure review activity, not openings or closures.',1,outer=TRUE,line=4,cex=.85)
}
png(file.path(out,'national_association_monthly.png'),width=1900,height=1250,res=150);draw();dev.off()
pdf(file.path(out,'national_association_monthly.pdf'),width=1900/150,height=1250/150);draw();dev.off()
