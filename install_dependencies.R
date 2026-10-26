lib <- file.path(getwd(), '.r-library')
dir.create(lib, showWarnings=FALSE)
.libPaths(c(lib, .libPaths()))
p <- c('fixest','data.table','jsonlite')
m <- p[!vapply(p, requireNamespace, logical(1), quietly=TRUE)]
if(length(m)) install.packages(m, repos='https://cloud.r-project.org', lib=lib)
