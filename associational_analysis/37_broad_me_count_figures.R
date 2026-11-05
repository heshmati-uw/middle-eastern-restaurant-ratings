args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'broad_me_monthly_counts.csv'));d$date<-as.Date(paste0(d$month,'-15'))
spec<-read.csv(file.path(out,'broad_me_count_figures.csv'));tot<-read.csv(file.path(out,'broad_me_count_totals.csv'))
groups<-c('ME','WPME','Medit');cols<-c('#B75A2A','#007F86','#6B52A3');votes<-c('Trump-majority','Other counties')
draw<-function(sp){
 s<-d[d$figure==sp$figure,];t<-tot[tot$figure==sp$figure,];ban<-sp$version=='Ban countries';both<-length(unique(s$vote_group))==2
 upper<-max(10,ceiling(max(s$restaurants)/if(both)500 else 20)*if(both)500 else 20)
 par(mar=c(4,5,4,1),oma=c(12,0,1,0),family='sans')
 plot(range(as.Date(c(paste0(sp$start,'-01'),'2017-06-15'))),c(0,upper*1.15),type='n',axes=FALSE,xlab='',ylab='Restaurants with at least one review')
 ticks<-pretty(c(0,upper));axis(2,at=ticks,las=1);axis.Date(1,at=seq(as.Date(paste0(sp$start,'-15')),as.Date('2017-04-15'),by=if(sp$start=='2015-01')'3 months' else '2 months'),format='%b\n%Y',cex.axis=.85);abline(h=ticks,col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray55');abline(v=as.Date('2017-01-27'),lty=2,col='gray55')
 ends<-data.frame()
 for(i in 1:3)for(j in seq_len(if(both)2 else 1)){
  z<-s[s$group==groups[i]&s$vote_group==votes[j],];z<-z[order(z$date),];lines(z$date,z$restaurants,col=cols[i],lwd=2.2,lty=j,pch=if(j==1)16 else 1,type='o',cex=.6)
  ends<-rbind(ends,data.frame(vote=j,value=tail(z$restaurants,1),color=cols[i]))
 }
 ord<-order(ends$value);ly<-ends$value
 for(k in 2:nrow(ends))ly[ord[k]]<-max(ly[ord[k]],ly[ord[k-1]]+upper*.032)
 for(k in 1:nrow(ends)){segments(as.Date('2017-04-18'),ends$value[k],as.Date('2017-05-02'),ly[k],col=ends$color[k],lty=ends$vote[k]);text(as.Date('2017-05-04'),ly[k],paste0(ends$value[k],if(both)if(ends$vote[k]==1)' T' else ' O' else ''),adj=0,col=ends$color[k],cex=.85)}
 legend('topleft',legend=c('Broadly ME positioned','WPME','Medit'),col=cols,lwd=2,bty='n',horiz=TRUE,cex=.95)
 if(both)legend('topright',legend=c('Trump-majority (T): solid, filled points','Other counties (O): dashed, open points'),col='gray25',lty=1:2,pch=c(16,1),lwd=2,bty='n',cex=.85)
 title(sprintf('Figure %d. %s | Monthly restaurant counts',sp$figure,if(ban)'Seven ban-country food lists' else 'National food lists'),line=2,cex.main=1.1)
 mtext(paste(sp$geography,'|',if(sp$start=='2015-01')'January 2015-April 2017' else 'December 2015-April 2017'),3,line=.5,cex=.85)
 note<-function(text,line,col='black')mtext(text,1,outer=TRUE,line=line,adj=0,at=.065,cex=.84,col=col)
 note(if(ban)'ME: ALL literal Middle Eastern primary tags, plus Persian, Syrian or Yemenite primary tags. No food requirement.' else 'ME: ALL literal Middle Eastern primary tags, plus qualifying national primary tags. No food requirement.',.5,cols[1])
 note(if(ban)'WPME: Mediterranean primary tag + at least one food linked to a ban country in any available review.' else 'WPME: Mediterranean primary tag + at least one food linked to the 12-country registry in any available review.',1.7,cols[2])
 note('Medit: ALL remaining Mediterranean-primary-tagged restaurants not already classified as WPME.',2.9,cols[3])
 for(j in seq_len(if(both)2 else 1)){tt<-t[t$vote_group==votes[j],];ns<-tt$restaurants[match(groups,tt$group)];note(sprintf('Unique restaurants, %s: ME %s; WPME %s; Medit %s.',votes[j],ns[1],ns[2],ns[3]),4.3+(j-1)*1.1)}
 note(if(ban)'Ban list: Iran, Iraq, Syria, Yemen, Libya, Somalia, Sudan. Non-ban national primary tags are excluded.' else 'National tags: Afghani, Armenian, Egyptian, Lebanese, Moroccan, Persian, Syrian and Yemenite.',6.6)
 note('Trump-majority: linked 2016 Trump vote share >50%; other counties: <=50%. Primary tags are snapshot attributes.',7.7)
 note('All eligible restaurants reviewed each month; no matching or fixed cohort. Any-date food evidence may postdate this period.',8.8)
 note('Raw counts measure review activity, not openings or closures. Jan 24 coverage (dotted); Jan 27 implementation (dashed).',9.9)
}
for(k in seq_len(nrow(spec))){sp<-spec[k,];stem<-sprintf('figure_%02d_counts',sp$figure)
 png(file.path(out,paste0(stem,'.png')),width=2200,height=1750,res=150);draw(sp);dev.off()
 pdf(file.path(out,paste0(stem,'.pdf')),width=2200/150,height=1750/150);draw(sp);dev.off()
 file.copy(file.path(out,paste0(stem,'.png')),file.path(out,paste0(sp$alias,'.png')),overwrite=TRUE)
 if(sp$figure!=1)file.copy(file.path(out,paste0(stem,'.pdf')),file.path(out,paste0(sp$alias,'.pdf')),overwrite=TRUE)
}
