#!/bin/sh

# source the jpackage helpers
VERBOSE=1
. /usr/share/java-utils/java-functions

# set JAVA_* environment variables
set_javacmd
check_java_env
set_jvm_dirs


DATADIR=/usr/share/java
CLASSPATH=${DATADIR}/bcprov.jar:${DATADIR}/bcmail.jar:${DATADIR}/bctsp.jar:${DATADIR}/itext.jar:${DATADIR}/itext-rups.jar:${DATADIR}/dom4j.jar:${DATADIR}/pdf-renderer.jar

set_options "-cp ${CLASSPATH}"

MAIN_CLASS="com.lowagie.rups.Rups"

run
