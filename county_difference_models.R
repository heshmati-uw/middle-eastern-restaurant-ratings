# Four-week group changes by county-vote stratum and direct between-stratum tests.
args<-commandArgs(trailingOnly=FALSE)
here<-dirname(normalizePath(sub('^--file=','',args[grepl('^--file=',args)])))
.libPaths(c(file.path(here,'.r-library'),.libPaths()))
suppressPackageStartupMessages({library(data.table);library(fixest);library(jsonlite)})
out<-here
cfg<-fromJSON(file.path(here,'shock_specifications.json'),simplifyVector=FALSE)
specs<-Filter(function(s)s$weeks==4,c(cfg$main_windows,cfg$sensitivity_windows))
w<-fread(file.path(out,'both_county_shock_weekly.csv'),colClasses=c(county_fips='character'))
w[,score_sum:=rating*reviews]
ssc_rule<-ssc(K.adj=TRUE,K.fixef='nonnested',G.adj=TRUE,t.df='min')
pairs<-list(c('ME','American'),c('WPME','American'),c('WPME','ME'))
strata<-list();differences<-list();descriptives<-list();changes<-list();models<-list()

for(spec in specs){
  z<-copy(w[(week>=spec$pre_start & week<=spec$pre_end)|
             (week>=spec$post_start & week<=spec$post_end)])
  z[,period:=ifelse(week<=spec$pre_end,'pre','post')]
  q<-z[,.(rating=sum(score_sum)/sum(reviews),reviews=sum(reviews),weeks=.N),
       by=.(gmap_id,group,county_fips,trump,period)]
  q<-dcast(q,gmap_id+group+county_fips+trump~period,value.var=c('rating','reviews','weeks'))
  q<-q[!is.na(rating_pre)&!is.na(rating_post)]
  q[,`:=`(change=rating_post-rating_pre,shock=spec$shock)]
  stopifnot(!anyDuplicated(q$gmap_id),q[,all(uniqueN(trump)==1),by=county_fips]$V1)
  changes[[length(changes)+1L]]<-q
  descriptives[[length(descriptives)+1L]]<-q[,.(restaurants=.N,counties=uniqueN(county_fips),
      pre=mean(rating_pre),post=mean(rating_post),change=mean(change),
      pre_reviews=sum(reviews_pre),post_reviews=sum(reviews_post)),by=.(shock,trump,group)]
  for(pair in pairs){
    d<-copy(q[group %chin% pair]);d[,treated:=as.integer(group==pair[1])]
    cell<-d[,.(n=.N,change=mean(change)),by=.(trump,treated)]
    stopifnot(nrow(cell)==4)
    contrasts<-numeric(2)
    for(t in 0:1){
      s<-d[trump==t]
      fit<-feols(change~treated,data=s,vcov=~county_fips,ssc=ssc_rule)
      ct<-as.matrix(coeftable(fit))['treated',];ci<-as.matrix(confint(fit))['treated',]
      contrasts[t+1]<-mean(s[treated==1]$change)-mean(s[treated==0]$change)
      stopifnot(abs(contrasts[t+1]-ct[1])<1e-12)
      stopifnot(abs(2*pt(abs(ct[3]),df=uniqueN(s$county_fips)-1,lower.tail=FALSE)-ct[4])<1e-12)
      strata[[length(strata)+1L]]<-data.table(shock=spec$shock,trump=t,
        comparison=paste(pair,collapse=' vs '),estimate=unname(ct[1]),se=unname(ct[2]),
        statistic=unname(ct[3]),p=unname(ct[4]),low=unname(ci[1]),high=unname(ci[2]),
        restaurants=nrow(s),counties=uniqueN(s$county_fips),
        treated_restaurants=sum(s$treated==1),control_restaurants=sum(s$treated==0))
      models[[paste(spec$shock,t,paste(pair,collapse='_'),sep='__')]]<-fit
    }
    # On period-level outcomes this is post × group × county type. Collapsing
    # to one change per business makes equal restaurant weights explicit.
    fit<-feols(change~treated*trump,data=d,vcov=~county_fips,ssc=ssc_rule)
    ct<-as.matrix(coeftable(fit))['treated:trump',]
    ci<-as.matrix(confint(fit))['treated:trump',]
    stopifnot(abs(contrasts[2]-contrasts[1]-ct[1])<1e-12)
    G<-uniqueN(d$county_fips)
    pneg<-pt(ct[3],df=G-1)
    stopifnot(abs(2*pt(abs(ct[3]),df=G-1,lower.tail=FALSE)-ct[4])<1e-12)
    differences[[length(differences)+1L]]<-data.table(shock=spec$shock,
      comparison=paste(pair,collapse=' vs '),trump_contrast=contrasts[2],nontrump_contrast=contrasts[1],
      difference=unname(ct[1]),se=unname(ct[2]),statistic=unname(ct[3]),p=unname(ct[4]),
      p_one_sided_negative=unname(pneg),low=unname(ci[1]),high=unname(ci[2]),
      restaurants=nrow(d),counties=G)
    models[[paste(spec$shock,'interaction',paste(pair,collapse='_'),sep='__')]]<-fit
  }
}
s<-rbindlist(strata);i<-rbindlist(differences)
s[,p_holm_three:=p.adjust(p,'holm'),by=.(shock,trump)]
i[,p_holm_all_six:=p.adjust(p,'holm')]
i[comparison=='ME vs American',p_holm_primary_two:=p.adjust(p,'holm')]
# Check that adding the non-Trump pool has not changed the previous Trump cases.
old<-fread(file.path(out,'election_ban_results.csv'))[weeks==4]
check<-merge(s[trump==1],old,by=c('shock','comparison'),suffixes=c('_new','_old'))
stopifnot(nrow(check)==6,all(abs(check$estimate_new-check$estimate_old)<1e-12),
          all(abs(check$se_new-check$se_old)<1e-12),all(abs(check$p_new-check$p_old)<1e-12),
          all(check$restaurants_new==check$restaurants_old))
fwrite(s,file.path(out,'county_stratum_four_week_results.csv'))
fwrite(i,file.path(out,'county_difference_four_week_tests.csv'))
fwrite(rbindlist(descriptives),file.path(out,'county_four_week_descriptives.csv'))
fwrite(rbindlist(changes),file.path(out,'county_four_week_restaurant_changes.csv'))
saveRDS(models,file.path(out,'county_four_week_models.rds'))
writeLines(capture.output(sessionInfo()),file.path(out,'county_difference_R_session.txt'))
cat('Non-Trump county comparisons:\n');print(s[trump==0])
cat('Direct tests: Trump contrast minus non-Trump contrast:\n');print(i)
