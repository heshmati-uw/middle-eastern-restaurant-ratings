args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'county_vote_monthly.csv'));d$date<-as.Date(paste0(d$month,'-15'))
totals<-read.csv(file.path(out,'county_vote_totals.csv'));coverage<-read.csv(file.path(out,'county_vote_coverage.csv'))
groups<-c('ME','Other ME','WPME','Medit');cols<-c('#B75A2A','#856344','#007F86','#6B52A3');votes<-c('Trump-majority','Other counties')
upper<-ceiling(max(d$restaurants[d$group%in%groups])/500)*500
draw<-function(version){
 s<-d[d$version==version,];t<-totals[totals$version==version,];cv<-coverage[coverage$version==version,];ban<-version=='Ban countries'
 par(mar=c(4,5,4,1),oma=c(15.5,0,1,0),family='sans')
 plot(range(as.Date(c('2015-12-01','2017-06-15'))),c(0,upper*1.14),type='n',axes=FALSE,xlab='',ylab='Restaurants with at least one review')
 ticks<-pretty(c(0,upper));axis(2,at=ticks,las=1);axis.Date(1,at=sort(unique(s$date)),format='%b\n%Y',cex.axis=.8);abline(h=ticks,col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray55');abline(v=as.Date('2017-01-27'),lty=2,col='gray55')
 ends<-data.frame()
 for(i in 1:4)for(j in 1:2){z<-s[s$group==groups[i]&s$vote_group==votes[j],];z<-z[order(z$date),];lines(z$date,z$restaurants,col=cols[i],lwd=2.2,lty=j,pch=if(j==1)16 else 1,type='o',cex=.55);ends<-rbind(ends,data.frame(group=groups[i],vote=j,value=tail(z$restaurants,1),color=cols[i]))}
 ord<-order(ends$value);ly<-ends$value
 ly[ord[1]]<-max(0,ly[ord[1]])
 for(k in 2:8)ly[ord[k]]<-max(ly[ord[k]],ly[ord[k-1]]+upper*.026)
 for(k in 1:8){segments(as.Date('2017-04-18'),ends$value[k],as.Date('2017-05-02'),ly[k],col=ends$color[k],lty=ends$vote[k]);text(as.Date('2017-05-04'),ly[k],paste0(ends$value[k],if(ends$vote[k]==1)' T' else ' O'),adj=0,col=ends$color[k],cex=.8)}
 legend('topleft',legend=groups,col=cols,lwd=2,bty='n',horiz=TRUE,cex=.95)
 legend('topright',legend=c('Trump-majority (T): solid, filled points','Other counties (O): dashed, open points'),col='gray25',lty=1:2,pch=c(16,1),lwd=2,bty='n',cex=.88)
 title(if(ban)'Seven ban-country associations | Both county vote groups' else 'National associations | Both county vote groups',line=2,cex.main=1.15)
 G<-cv$active_counties[match(votes,cv$vote_group)]
 mtext(sprintf('December 2015-April 2017 | %d Trump-majority counties and %d other counties represented | Raw counts',G[1],G[2]),3,line=.5,cex=.9)
 note<-function(text,line,col='black',bold=FALSE)mtext(text,1,outer=TRUE,line=line,adj=0,at=.065,cex=.84,col=col,font=if(bold)2 else 1)
 note(if(ban)'FOOD LISTS: Iran, Iraq, Syria, Yemen, Libya, Somalia and Sudan' else 'FOOD LISTS: existing 12-country registry; identical category and food rules in both county vote groups',.5,bold=TRUE)
 note(if(ban)'ME: Persian, Syrian or Yemenite primary tag OR a Middle Eastern primary tag + at least one ban-country-listed food mention.' else 'ME: a qualifying national primary tag OR a Middle Eastern primary tag + at least one country-listed food mention.',1.8,cols[1])
 note('Other ME: all remaining Middle Eastern-primary-tagged restaurants not already counted in ME.',3,cols[2])
 note(if(ban)'WPME: Mediterranean primary tag + at least one ban-country-listed food mention; the same food rule as literal ME.' else 'WPME: Mediterranean primary tag + at least one country-listed food mention; the same food rule as literal ME.',4.2,cols[3])
 note('Medit: all remaining Mediterranean-primary-tagged restaurants not already counted in WPME.',5.4,cols[4])
 for(j in 1:2){tt<-t[t$vote_group==votes[j],];ns<-tt$active_restaurants[match(groups,tt$group)];note(sprintf('Unique restaurants, %s: ME %s; Other ME %s; WPME %s; Medit %s.',votes[j],ns[1],ns[2],ns[3],ns[4]),6.8+(j-1)*1.1)}
 note(if(ban)'Non-ban national primary tags are excluded in both county groups. Literal Middle Eastern tags remain eligible through food.' else 'National tags: Afghani, Armenian, Egyptian, Lebanese, Moroccan, Persian, Syrian and Yemenite; these qualify directly.',9)
 note('Trump-majority: linked 2016 Trump vote share >50%; other counties: <=50%. Same sample rules, different population sizes.',10.1)
 note('Any-date food evidence may postdate April 2017. All restaurants reviewed each month; no matching or balanced review cohort.',11.2)
 note('Raw counts are not rates or ratings. End labels show April counts (T/O); full-period totals above are not fixed monthly cohorts.',12.3)
 note('Jan 24 coverage (dotted); Jan 27 implementation (dashed). Counts reflect review activity, not openings or closures. No Americans.',13.4)
}
for(v in c('Broad','Ban countries')){tag<-if(v=='Broad')'broad' else 'ban';png(file.path(out,paste0('county_vote_',tag,'.png')),width=2200,height=1850,res=150);draw(v);dev.off();pdf(file.path(out,paste0('county_vote_',tag,'.pdf')),width=2200/150,height=1850/150);draw(v);dev.off()}
