args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'positioning_anydate_monthly.csv'));d$date<-as.Date(paste0(d$month,'-15'))
draw<-function(v){s<-d[d$version==v,];groups<-c('ME','WPME','All other Mediterranean restaurants');cols<-c('#B75A2A','#007F86','#6B52A3')
 par(mar=c(4,5,4,1),oma=c(7,0,3,0),family='sans')
 plot(range(as.Date(c('2015-12-01','2017-04-30'))),c(0,80),type='n',axes=FALSE,xlab='',ylab='Restaurants with at least one review')
 axis(2,at=seq(0,70,10),las=1);axis.Date(1,at=sort(unique(s$date)),format='%b\n%Y',cex.axis=.8);abline(h=seq(0,70,10),col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray35');abline(v=as.Date('2017-01-27'),lty=2,col='gray35')
 for(i in 1:3){z<-s[s$group==groups[i],];lines(z$date,z$restaurants,col=cols[i],lwd=2,pch=16,type='o',cex=.75)}
 # Label every monthly count; separate labels when series are close.
 for(day in sort(unique(s$date))){z<-s[s$date==day,];vals<-z$restaurants[match(groups,z$group)];ly<-vals+2.2;order<-order(vals)
  ly[order[1]]<-vals[order[1]]-2.2
  for(j in 2:3)ly[order[j]]<-max(ly[order[j]],ly[order[j-1]]+3)
  for(i in 1:3)text(day,ly[i],labels=vals[i],col=cols[i],cex=.8,xpd=TRUE)
 }
 legend('topleft',legend=c('ME: explicit ME or national label','WPME: Mediterranean label + qualifying ME food','All other Mediterranean restaurants'),col=cols,pch=16,lty=1,bty='n',cex=.9)
 title(paste(v,'ME food dictionary | Any-date food evidence'),line=2,cex.main=1.2)
 mtext('WPME qualifies from at least one dish mention at ANY available review date; no November 8 cutoff',3,line=.5,cex=.9)
 mtext('Monthly counts include ALL restaurants with reviews in that month; no fixed or balanced review cohort.',1,outer=TRUE,line=.5,cex=.9)
 mtext('Same seven Trump-majority counties; December 2015-April 2017; no American restaurants or matching.',1,outer=TRUE,line=1.7,cex=.9)
 mtext('ME remains label-defined. All other Mediterranean includes every Mediterranean-labeled restaurant outside WPME.',1,outer=TRUE,line=2.9,cex=.85)
 mtext('Any-date evidence can come AFTER April 2017 and is applied retrospectively to earlier months; not historical menu verification.',1,outer=TRUE,line=4.1,cex=.85)
 mtext('Jan 24 coverage (dotted); Jan 27 implementation (dashed). January combines pre/post days; counts describe review activity.',1,outer=TRUE,line=5.3,cex=.85)
}
for(v in c('Broader','Seven-country')){tag<-if(v=='Broader')'broader' else 'seven_country';png(file.path(out,paste0('positioning_anydate_',tag,'.png')),width=1900,height=1250,res=150);draw(v);dev.off();pdf(file.path(out,paste0('positioning_anydate_',tag,'.pdf')),width=1900/150,height=1250/150);draw(v);dev.off()}
