args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'broad_me_monthly_ratings.csv'));d$date<-as.Date(paste0(d$month,'-15'));tot<-read.csv(file.path(out,'broad_me_rating_totals.csv'))
groups<-c('ME','WPME','Medit');cols<-c('#B75A2A','#007F86','#6B52A3');votes<-c('Trump-majority','Other counties')
yl<-range(unlist(d[c('restaurant_weighted_mean','review_weighted_mean')]));yl<-c(floor((yl[1]-.08)*10)/10,ceiling((yl[2]+.08)*10)/10)
draw<-function(version,weight,num){
 s<-d[d$version==version,];t<-tot[tot$version==version,];ban<-version=='Ban countries';rw<-weight=='restaurant_weighted_mean'
 par(mar=c(4,5,4,1),oma=c(14,0,1,0),family='sans')
 plot(range(as.Date(c('2015-01-01','2017-06-15'))),c(yl[1],yl[2]+.17),type='n',axes=FALSE,xlab='',ylab='Mean rating (1-5 stars)')
 ticks<-seq(yl[1],yl[2],by=.1);axis(2,at=ticks,las=1);axis.Date(1,at=seq(as.Date('2015-01-15'),as.Date('2017-04-15'),by='3 months'),format='%b\n%Y',cex.axis=.85);abline(h=ticks,col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray55');abline(v=as.Date('2017-01-27'),lty=2,col='gray55')
 ends<-data.frame()
 for(i in 1:3)for(j in 1:2){z<-s[s$group==groups[i]&s$vote_group==votes[j],];z<-z[order(z$date),];lines(z$date,z[[weight]],col=cols[i],lwd=2.1,lty=j,pch=if(j==1)16 else 1,type='o',cex=.6);ends<-rbind(ends,data.frame(vote=j,value=tail(z[[weight]],1),color=cols[i]))}
 ord<-order(ends$value);ly<-ends$value
 for(k in 2:6)ly[ord[k]]<-max(ly[ord[k]],ly[ord[k-1]]+.032)
 for(k in 1:6){segments(as.Date('2017-04-18'),ends$value[k],as.Date('2017-05-02'),ly[k],col=ends$color[k],lty=ends$vote[k]);text(as.Date('2017-05-04'),ly[k],paste0(sprintf('%.2f',ends$value[k]),if(ends$vote[k]==1)' T' else ' O'),adj=0,col=ends$color[k],cex=.85)}
 legend('topleft',legend=c('Broadly ME positioned','WPME','Medit'),col=cols,lwd=2,bty='n',horiz=TRUE,cex=.95)
 legend('topright',legend=c('Trump-majority (T): solid, filled points','Other counties (O): dashed, open points'),col='gray25',lty=1:2,pch=c(16,1),lwd=2,bty='n',cex=.85)
 title(sprintf('Figure %d. %s | Monthly mean ratings',num,if(ban)'Seven ban-country food lists' else 'National food lists'),line=2,cex.main=1.1)
 mtext(paste('All available counties | January 2015-April 2017 |',if(rw)'Equal weight per restaurant within each month' else 'Equal weight per review within each month'),3,line=.5,cex=.85)
 note<-function(text,line,col='black')mtext(text,1,outer=TRUE,line=line,adj=0,at=.065,cex=.82,col=col)
 note(if(ban)'ME: ALL literal Middle Eastern primary tags + Persian, Syrian or Yemenite primary tags. No food requirement.' else 'ME: ALL literal Middle Eastern primary tags + qualifying national primary tags. No food requirement.',.5,cols[1])
 note(if(ban)'WPME: Mediterranean primary tag + at least one food linked to a ban country in any available review.' else 'WPME: Mediterranean primary tag + at least one food linked to the 12-country registry in any available review.',1.6,cols[2])
 note('Medit: ALL remaining Mediterranean-primary-tagged restaurants not already classified as WPME.',2.7,cols[3])
 for(j in 1:2){tt<-t[t$vote_group==votes[j],];nn<-tt$restaurants[match(groups,tt$group)];rr<-tt$reviews[match(groups,tt$group)];note(sprintf('%s | Unique restaurants: ME %s; WPME %s; Medit %s. Reviews: ME %s; WPME %s; Medit %s.',votes[j],nn[1],nn[2],nn[3],format(rr[1],big.mark=','),format(rr[2],big.mark=','),format(rr[3],big.mark=',')),4.1+(j-1)*1.1)}
 note(if(rw)'Each point averages restaurant-month means; a restaurant with one review has the same weight as one with 100.' else 'Each point averages all reviews; restaurants with more reviews receive proportionately more weight.',6.6)
 note('Both use the identical restaurant-month samples as Figures 7-8. Full-period totals above are not fixed monthly cohorts.',7.7)
 note(if(ban)'Ban list: Iran, Iraq, Syria, Yemen, Libya, Somalia, Sudan. Non-ban national primary tags are excluded.' else 'National tags: Afghani, Armenian, Egyptian, Lebanese, Moroccan, Persian, Syrian and Yemenite.',8.8)
 note('Trump-majority: linked 2016 Trump share >50%; other counties: <=50%. Snapshot labels; retrospective any-date food evidence.',9.9)
 note('Raw, unadjusted descriptive means. Monthly composition can change; no matching, fixed cohort or causal interpretation.',11)
 note('Jan 24 coverage (dotted); Jan 27 implementation (dashed). End labels show April means. Axis is restricted for readability.',12.1)
}
num<-8
for(weight in c('restaurant_weighted_mean','review_weighted_mean'))for(version in c('Broad','Ban countries')){
 num<-num+1;stem<-sprintf('figure_%02d_ratings',num)
 png(file.path(out,paste0(stem,'.png')),width=2200,height=1850,res=150);draw(version,weight,num);dev.off()
 pdf(file.path(out,paste0(stem,'.pdf')),width=2200/150,height=1850/150);draw(version,weight,num);dev.off()
}
