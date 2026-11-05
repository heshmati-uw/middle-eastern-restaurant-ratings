args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'all_trump_monthly.csv'));d$date<-as.Date(paste0(d$month,'-15'))
totals<-read.csv(file.path(out,'all_trump_totals.csv'));coverage<-read.csv(file.path(out,'all_trump_county_coverage.csv'),colClasses=c(county_fips='character'))
groups<-c('ME','Other ME','WPME','Medit');cols<-c('#B75A2A','#856344','#007F86','#6B52A3')
upper<-ceiling(max(d$restaurants[d$group%in%groups])/50)*50
draw<-function(version){
 s<-d[d$version==version,];t<-totals[totals$version==version,];ban<-version=='Ban countries';G<-sum(coverage$version==version)
 par(mar=c(4,5,4,1),oma=c(13.5,0,1,0),family='sans')
 plot(range(as.Date(c('2015-12-01','2017-04-30'))),c(0,upper*1.25),type='n',axes=FALSE,xlab='',ylab='Restaurants with at least one review')
 ticks<-pretty(c(0,upper));axis(2,at=ticks,las=1);axis.Date(1,at=sort(unique(s$date)),format='%b\n%Y',cex.axis=.8);abline(h=ticks,col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray35');abline(v=as.Date('2017-01-27'),lty=2,col='gray35')
 for(i in 1:4){z<-s[s$group==groups[i],];lines(z$date,z$restaurants,col=cols[i],lwd=2,pch=15+i,type='o',cex=.7)}
 for(day in sort(unique(s$date))){z<-s[s$date==day,];vals<-z$restaurants[match(groups,z$group)];ly<-vals+upper*.02;ord<-order(vals)
  ly[ord[1]]<-vals[ord[1]]-upper*.025
  for(j in 2:4)ly[ord[j]]<-max(ly[ord[j]],ly[ord[j-1]]+upper*.04)
  for(i in 1:4)text(day,ly[i],labels=vals[i],col=cols[i],cex=.75,xpd=TRUE)
 }
 legend('topleft',legend=groups,col=cols,pch=16:19,lty=1,bty='n',cex=.95,horiz=TRUE)
 title(if(ban)'Seven ban-country associations | All available Trump-majority counties' else 'National associations | All available Trump-majority counties',line=2,cex.main=1.1)
 mtext(sprintf('December 2015-April 2017 | %d counties represented during the full period | Monthly sample varies',G),3,line=.5,cex=.9)
 note<-function(text,line,col='black',bold=FALSE)mtext(text,1,outer=TRUE,line=line,adj=0,at=.065,cex=.84,col=col,font=if(bold)2 else 1)
 note(if(ban)'FOOD LISTS: Iran, Iraq, Syria, Yemen, Libya, Somalia and Sudan' else 'FOOD LISTS: existing 12-country registry; geographic scope expanded, food definitions unchanged',.5,bold=TRUE)
 note(if(ban)'ME: Persian, Syrian or Yemenite primary tag OR a Middle Eastern primary tag + at least one ban-country-listed food mention.' else 'ME: a qualifying national primary tag OR a Middle Eastern primary tag + at least one country-listed food mention.',1.8,cols[1])
 note('Other ME: all remaining Middle Eastern-primary-tagged restaurants not already counted in ME.',3,cols[2])
 note(if(ban)'WPME: Mediterranean primary tag + at least one ban-country-listed food mention; the same food rule as literal ME.' else 'WPME: Mediterranean primary tag + at least one country-listed food mention; the same food rule as literal ME.',4.2,cols[3])
 note('Medit: all remaining Mediterranean-primary-tagged restaurants not already counted in WPME.',5.4,cols[4])
 ns<-t$active_restaurants[match(groups,t$group)]
 note(sprintf('Unique restaurants across the full period: ME %d; Other ME %d; WPME %d; Medit %d. These are not fixed monthly cohorts.',ns[1],ns[2],ns[3],ns[4]),6.8)
 note(if(ban)sprintf('Non-ban national primary tags excluded: %d review-active restaurants. Literal Middle Eastern primary tags remain eligible.',t$active_restaurants[t$group=='Excluded other national tags']) else 'National tags: Afghani, Armenian, Egyptian, Lebanese, Moroccan, Persian, Syrian and Yemenite; these qualify directly.',7.9)
 note('Food evidence uses any available review date, including after April 2017; shared dishes count. Primary tags are snapshot labels.',9)
 note('Trump-majority means 2016 Trump vote share >50%. No matching, county peer requirement or balanced review cohort; no Americans.',10.1)
 note('Jan 24 coverage (dotted); Jan 27 implementation (dashed). Counts describe review activity, not openings or closures.',11.2)
 note('Geographic universe: 277 counties with 1,062 eligible metadata restaurants; plotted counties require reviews in this period.',12.3)
}
for(v in c('Broad','Ban countries')){tag<-if(v=='Broad')'broad' else 'ban';png(file.path(out,paste0('all_trump_',tag,'.png')),width=2000,height=1700,res=150);draw(v);dev.off();pdf(file.path(out,paste0('all_trump_',tag,'.pdf')),width=2000/150,height=1700/150);draw(v);dev.off()}
