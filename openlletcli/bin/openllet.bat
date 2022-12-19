@REM ----------------------------------------------------------------------------
@REM  Copyright 2001-2006 The Apache Software Foundation.
@REM
@REM  Licensed under the Apache License, Version 2.0 (the "License");
@REM  you may not use this file except in compliance with the License.
@REM  You may obtain a copy of the License at
@REM
@REM       http://www.apache.org/licenses/LICENSE-2.0
@REM
@REM  Unless required by applicable law or agreed to in writing, software
@REM  distributed under the License is distributed on an "AS IS" BASIS,
@REM  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@REM  See the License for the specific language governing permissions and
@REM  limitations under the License.
@REM ----------------------------------------------------------------------------
@REM
@REM   Copyright (c) 2001-2006 The Apache Software Foundation.  All rights
@REM   reserved.

@echo off

set ERROR_CODE=0

:init
@REM Decide how to startup depending on the version of windows

@REM -- Win98ME
if NOT "%OS%"=="Windows_NT" goto Win9xArg

@REM set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" @setlocal

@REM -- 4NT shell
if "%eval[2+2]" == "4" goto 4NTArgs

@REM -- Regular WinNT shell
set CMD_LINE_ARGS=%*
goto WinNTGetScriptDir

@REM The 4NT Shell from jp software
:4NTArgs
set CMD_LINE_ARGS=%$
goto WinNTGetScriptDir

:Win9xArg
@REM Slurp the command line arguments.  This loop allows for an unlimited number
@REM of arguments (up to the command line limit, anyway).
set CMD_LINE_ARGS=
:Win9xApp
if %1a==a goto Win9xGetScriptDir
set CMD_LINE_ARGS=%CMD_LINE_ARGS% %1
shift
goto Win9xApp

:Win9xGetScriptDir
set SAVEDIR=%CD%
%0\
cd %0\..\.. 
set BASEDIR=%CD%
cd %SAVEDIR%
set SAVE_DIR=
goto repoSetup

:WinNTGetScriptDir
set BASEDIR=%~dp0\..

:repoSetup
set REPO=


if "%JAVACMD%"=="" set JAVACMD=java

if "%REPO%"=="" set REPO=%BASEDIR%\lib

set CLASSPATH="%BASEDIR%"\etc;"%REPO%"\openllet-owlapi-2.6.5.jar;"%REPO%"\openllet-core-2.6.5.jar;"%REPO%"\openllet-functions-2.6.5.jar;"%REPO%"\openllet-query-2.6.5.jar;"%REPO%"\antlr-runtime-3.5.3.jar;"%REPO%"\owlapi-distribution-5.1.20.jar;"%REPO%"\owlapi-compatibility-5.1.20.jar;"%REPO%"\owlapi-apibinding-5.1.20.jar;"%REPO%"\owlapi-api-5.1.20.jar;"%REPO%"\javax.inject-1.jar;"%REPO%"\owlapi-impl-5.1.20.jar;"%REPO%"\owlapi-parsers-5.1.20.jar;"%REPO%"\owlapi-oboformat-5.1.20.jar;"%REPO%"\owlapi-tools-5.1.20.jar;"%REPO%"\owlapi-rio-5.1.20.jar;"%REPO%"\jackson-core-2.9.10.jar;"%REPO%"\jackson-databind-2.9.10.jar;"%REPO%"\jackson-annotations-2.9.10.jar;"%REPO%"\commons-rdf-api-0.5.0.jar;"%REPO%"\xz-1.6.jar;"%REPO%"\jcl-over-slf4j-1.7.36.jar;"%REPO%"\rdf4j-model-3.7.4.jar;"%REPO%"\rdf4j-model-api-3.7.4.jar;"%REPO%"\rdf4j-model-vocabulary-3.7.4.jar;"%REPO%"\rdf4j-rio-api-3.7.4.jar;"%REPO%"\rdf4j-rio-languages-3.7.4.jar;"%REPO%"\rdf4j-rio-datatypes-3.7.4.jar;"%REPO%"\rdf4j-rio-binary-3.7.4.jar;"%REPO%"\rdf4j-rio-n3-3.7.4.jar;"%REPO%"\rdf4j-rio-nquads-3.7.4.jar;"%REPO%"\rdf4j-rio-ntriples-3.7.4.jar;"%REPO%"\rdf4j-rio-rdfjson-3.7.4.jar;"%REPO%"\rdf4j-rio-jsonld-3.7.4.jar;"%REPO%"\httpclient-4.5.13.jar;"%REPO%"\httpcore-4.4.13.jar;"%REPO%"\httpclient-cache-4.5.13.jar;"%REPO%"\rdf4j-rio-rdfxml-3.7.4.jar;"%REPO%"\rdf4j-rio-trix-3.7.4.jar;"%REPO%"\rdf4j-rio-turtle-3.7.4.jar;"%REPO%"\rdf4j-rio-trig-3.7.4.jar;"%REPO%"\rdf4j-rio-hdt-3.7.4.jar;"%REPO%"\rdf4j-util-3.7.4.jar;"%REPO%"\jsonld-java-0.12.3.jar;"%REPO%"\httpclient-osgi-4.5.6.jar;"%REPO%"\httpmime-4.5.6.jar;"%REPO%"\fluent-hc-4.5.6.jar;"%REPO%"\httpcore-osgi-4.4.10.jar;"%REPO%"\httpcore-nio-4.4.10.jar;"%REPO%"\hppcrt-0.7.5.jar;"%REPO%"\caffeine-2.8.1.jar;"%REPO%"\checker-qual-3.1.0.jar;"%REPO%"\error_prone_annotations-2.3.4.jar;"%REPO%"\guava-27.1-jre.jar;"%REPO%"\failureaccess-1.0.1.jar;"%REPO%"\listenablefuture-9999.0-empty-to-avoid-conflict-with-guava.jar;"%REPO%"\j2objc-annotations-1.1.jar;"%REPO%"\animal-sniffer-annotations-1.17.jar;"%REPO%"\jsr305-3.0.2.jar;"%REPO%"\commons-io-2.6.jar;"%REPO%"\jaxb-api-2.3.0.jar;"%REPO%"\openllet-pellint-2.6.5.jar;"%REPO%"\openllet-jena-2.6.5.jar;"%REPO%"\jena-core-3.10.0.jar;"%REPO%"\jena-iri-3.10.0.jar;"%REPO%"\commons-cli-1.4.jar;"%REPO%"\commons-codec-1.11.jar;"%REPO%"\jena-base-3.10.0.jar;"%REPO%"\commons-csv-1.5.jar;"%REPO%"\commons-compress-1.17.jar;"%REPO%"\collection-0.7.jar;"%REPO%"\jena-arq-3.10.0.jar;"%REPO%"\jena-shaded-guava-3.10.0.jar;"%REPO%"\libthrift-0.17.0.jar;"%REPO%"\commons-lang3-3.4.jar;"%REPO%"\jgrapht-ext-1.1.0.jar;"%REPO%"\jgrapht-core-1.1.0.jar;"%REPO%"\jgrapht-io-1.1.0.jar;"%REPO%"\antlr4-runtime-4.6.jar;"%REPO%"\jgraphx-2.0.0.1.jar;"%REPO%"\jgraph-5.13.0.0.jar;"%REPO%"\openllet-modularity-2.6.5.jar;"%REPO%"\openllet-explanation-2.6.5.jar;"%REPO%"\slf4j-simple-1.7.36.jar;"%REPO%"\slf4j-api-1.7.36.jar;"%REPO%"\openllet-cli-2.6.5.jar

set ENDORSED_DIR=
if NOT "%ENDORSED_DIR%" == "" set CLASSPATH="%BASEDIR%"\%ENDORSED_DIR%\*;%CLASSPATH%

if NOT "%CLASSPATH_PREFIX%" == "" set CLASSPATH=%CLASSPATH_PREFIX%;%CLASSPATH%

@REM Reaching here means variables are defined and arguments have been captured
:endInit

%JAVACMD% %JAVA_OPTS%  -classpath %CLASSPATH% -Dapp.name="openllet" -Dapp.repo="%REPO%" -Dapp.home="%BASEDIR%" -Dbasedir="%BASEDIR%" openllet.Openllet %CMD_LINE_ARGS%
if %ERRORLEVEL% NEQ 0 goto error
goto end

:error
if "%OS%"=="Windows_NT" @endlocal
set ERROR_CODE=%ERRORLEVEL%

:end
@REM set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" goto endNT

@REM For old DOS remove the set variables from ENV - we assume they were not set
@REM before we started - at least we don't leave any baggage around
set CMD_LINE_ARGS=
goto postExec

:endNT
@REM If error code is set to 1 then the endlocal was done already in :error.
if %ERROR_CODE% EQU 0 @endlocal


:postExec

if "%FORCE_EXIT_ON_ERROR%" == "on" (
  if %ERROR_CODE% NEQ 0 exit %ERROR_CODE%
)

exit /B %ERROR_CODE%
