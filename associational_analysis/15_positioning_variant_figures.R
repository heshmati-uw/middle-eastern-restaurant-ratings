args<-commandArgs(FALSE);root<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])));out<-file.path(root,'outputs')
d<-read.csv(file.path(out,'positioning_variants_monthly.csv'));d$date<-as.Date(paste0(d$month,'-15'))
totals<-read.csv(file.path(out,'positioning_variants_totals.csv'));counts<-read.csv(file.path(out,'positioning_variants_prepost.csv'))
salad<-read.csv(file.path(out,'positioning_variants_salad_sensitivity.csv'))
draw<-function(v){s<-d[d$version==v,];n<-totals[totals$version==v,];broad<-v%in%c('V1','V2');positive<-v%in%c('V1','V3');groups<-c('ME','WPME','Other Mediterranean');cols<-c('#B75A2A','#007F86','#6B52A3')
 par(mar=c(4,5,4,1),oma=c(8,0,3,0),family='sans')
 plot(range(as.Date(c('2015-12-01','2017-04-30'))),c(0,80),type='n',axes=FALSE,xlab='',ylab='Restaurants with at least one review')
 axis(2,at=seq(0,70,10),las=1);axis.Date(1,at=sort(unique(s$date)),format='%b\n%Y',cex.axis=.8);abline(h=seq(0,70,10),col='gray92')
 abline(v=as.Date('2017-01-24'),lty=3,col='gray35');abline(v=as.Date('2017-01-27'),lty=2,col='gray35')
 for(i in 1:3){z<-s[s$group==groups[i],];lines(z$date,z$restaurants,col=cols[i],lwd=2,pch=16,type='o',cex=.75)}
 names<-c('ME: explicit ME or national label','WPME: Mediterranean label + qualifying ME food',if(positive)'Other Med: positive Greek/Italian/Spanish evidence' else 'Other Med: no qualifying ME food observed')
 ns<-n$active_any_month[match(groups,n$group)]
 legend('topleft',legend=paste0(names,' (N = ',ns,')'),col=cols,pch=16,lty=1,bty='n',cex=.85)
 title(paste(v,if(broad)'Broader ME food dictionary' else 'Seven-country food dictionary',sep=' | '),line=2,cex.main=1.2)
 mtext(if(positive)'Positive-evidence Mediterranean comparison; insufficient food evidence remains unclassified' else 'Residual Mediterranean comparison; absence of ME mentions does not establish non-ME cuisine',3,line=.5,cex=.9)
 un<-n$active_any_month[n$group=='Unclassified'];mx<-max(s$restaurants[s$group=='Unclassified']);nohist<-n$without_pre_election_text[n$group=='Other Mediterranean']
 mtext(sprintf('Same seven Trump-majority counties; no American restaurants. N = unique restaurants active at any point in Dec 2015-Apr 2017.'),1,outer=TRUE,line=.5,cex=.85)
 mtext('ME pools literal Middle Eastern + qualifying national labels. WPME is a positioning proxy, not measured perceived whiteness.',1,outer=TRUE,line=1.7,cex=.85)
 mtext('Food evidence: at least one pre-Nov 8, 2016 review mention. No same-county culinary peer or later outcome-review requirement.',1,outer=TRUE,line=2.9,cex=.85)
 mtext(sprintf('Unclassified: %s unique restaurants (monthly maximum %s); other-Med group without pre-election text: %s.',un,mx,nohist),1,outer=TRUE,line=4.1,cex=.85)
 ss<-salad[salad$version==v,]
 mtext(sprintf('Positive other-Med evidence pool: %s; only %s excluding Greek-salad-only evidence. Both food types present enter WPME.',ss$positive_other_med_main,ss$positive_other_med_excluding_greek_salad_only),1,outer=TRUE,line=5.3,cex=.85)
 mtext('Jan 24 coverage (dotted); Jan 27 implementation (dashed). January combines pre/post days; counts describe review activity.',1,outer=TRUE,line=6.5,cex=.85)
}
for(v in paste0('V',1:4)){png(file.path(out,paste0('positioning_variants_',v,'.png')),width=1900,height=1300,res=150);draw(v);dev.off();pdf(file.path(out,paste0('positioning_variants_',v,'.pdf')),width=1900/150,height=1300/150);draw(v);dev.off()}

