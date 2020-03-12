#!/usr/bin/env bash

echo "Preparing zip archive with RTCC ansible scripts"

mvn clean install com.netcracker.om.tls.maven.plugin:dtrust-maven-plugin:3.3.2:dtrust -Ddtrust.approve.build.fail=false
