/*
 * SonarLint Core - Implementation
 * Copyright (C) 2016-2023 SonarSource SA
 * mailto:info AT sonarsource DOT com
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */
package mediumtest;

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import org.sonarsource.sonarlint.core.StandaloneSonarLintEngineImpl;
import org.sonarsource.sonarlint.core.analysis.api.ClientInputFile;
import org.sonarsource.sonarlint.core.client.api.common.analysis.Issue;
import org.sonarsource.sonarlint.core.client.api.standalone.StandaloneAnalysisConfiguration;
import org.sonarsource.sonarlint.core.client.api.standalone.StandaloneGlobalConfiguration;
import org.sonarsource.sonarlint.core.commons.Language;

import testutils.OnDiskTestClientInputFile;
import testutils.PluginLocator;

public class StandaloneIssueMediumTests4 {

	private static StandaloneSonarLintEngineImpl sonarlint;

	public static void main(String args[]) throws Exception {
		var configBuilder = StandaloneGlobalConfiguration.builder().addPlugin(PluginLocator.getJavaPluginPath())
				.addPlugin(PluginLocator.getPythonPluginPath()).addEnabledLanguages(Language.JAVA, Language.PYTHON);
		
		sonarlint = new StandaloneSonarLintEngineImpl(configBuilder.build());

		File rootDir = new File("/Users/nelsonmbigili/Desktop/Spring 2026/Software Analysis/SoftwareAnalytics-ReplicationStudy-CodeReadability/datasets/fileTemp");
		
		File[] projects = rootDir.listFiles();
		
		for (File project: projects) {
			if (!containsCSVOrIsEmpty(project)) {
				System.out.println("Processing project "+project.getName());
				processProject(project,sonarlint,Language.JAVA,"Test.java");	
			}
			
		}
		
		sonarlint.stop();
	}

	private static boolean containsCSVOrIsEmpty(File project) {
		File[] files = project.listFiles();
		if (files.length == 0 ) {
			return true;
		}
		for (File f: files) {
			if (f.getName().endsWith(".csv")) {
				return true;
			}
		}
		return false;
	}

	private static void processProject(File project, StandaloneSonarLintEngineImpl sonarlint,
			Language language,String testFileName) throws Exception {
		
		File baseDirBefore = getBaseDir(project,"before");
		
		File baseDirAfter = getBaseDir(project,"after");
				
		List<Issue> issuesBefore = processProject1(project,baseDirBefore,sonarlint,language,testFileName);
		List<Issue> issuesAfter = processProject1(project,baseDirAfter,sonarlint,language,testFileName);
		
		writeIssues(issuesBefore,project,"before");
		writeIssues(issuesAfter,project,"after");
		
	}

	private static void writeIssues(List<Issue> issues, File project, String beforeAfter) throws Exception {
		File file = new File(project.getAbsolutePath()+"/sonarLintAnalysis_"+beforeAfter+".csv");
		PrintWriter pw = new PrintWriter(file);
		pw.println("rule key,start line,end line,severity,message,type");
		for (Issue issue:issues) {
			pw.println(issue.getRuleKey()+","+issue.getStartLine()+","+issue.getEndLine()+","+issue.getSeverity().name()
					+","+issue.getMessage()+","+issue.getType().name());
		}
		pw.close();
	}

	private static List<Issue> processProject1(File project, File baseDir,
			StandaloneSonarLintEngineImpl sonarlint2, Language language, String testFileName) {
		File file = baseDir.listFiles()[0];
		
		String relativePath = file.getName();
		
		//boolean isTest = relativePath.endsWith(testFileName)?true:false;
		boolean isTest = false;
		
		Charset encoding = StandardCharsets.UTF_8;
	
		
		ClientInputFile inputFile = new OnDiskTestClientInputFile(file.toPath(), relativePath, isTest, encoding, language);

		final List<Issue> issues = new ArrayList<>();
		sonarlint.analyze(
				StandaloneAnalysisConfiguration.builder().setBaseDir(baseDir.toPath()).addInputFile(inputFile).build(),
				issues::add, null, null);		
		return issues;
	}

	private static File getBaseDir(File project,String beforeAfter) {
		File anterior = new File(project.getAbsolutePath()+"/"+beforeAfter);
		while (project.isDirectory()) {
			if (anterior.listFiles()[0].isDirectory()) {
				anterior = anterior.listFiles()[0];	
			} else {
				return anterior;
			}
			
		}
		return anterior;
	}



}
