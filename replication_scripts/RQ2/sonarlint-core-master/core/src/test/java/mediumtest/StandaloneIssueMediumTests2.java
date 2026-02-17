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

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.tuple;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.annotation.Nullable;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.SystemUtils;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.sonarsource.sonarlint.core.NodeJsHelper;
import org.sonarsource.sonarlint.core.StandaloneSonarLintEngineImpl;
import org.sonarsource.sonarlint.core.analysis.api.ClientInputFile;
import org.sonarsource.sonarlint.core.client.api.common.analysis.Issue;
import org.sonarsource.sonarlint.core.client.api.standalone.StandaloneAnalysisConfiguration;
import org.sonarsource.sonarlint.core.client.api.standalone.StandaloneGlobalConfiguration;
import org.sonarsource.sonarlint.core.commons.IssueSeverity;
import org.sonarsource.sonarlint.core.commons.Language;

import testutils.OnDiskTestClientInputFile;
import testutils.PluginLocator;

class StandaloneIssueMediumTests2 {

  private static Path sonarlintUserHome;
  private static Path fakeTypeScriptProjectPath;

  private static final String A_JAVA_FILE_PATH = "Foo.java";
  private static StandaloneSonarLintEngineImpl sonarlint;
  private File baseDir;
  // commercial plugins might not be available
  // (if you pass -Dcommercial to maven, a profile will be activated that downloads the commercial plugins)
  private static final boolean COMMERCIAL_ENABLED = System.getProperty("commercial") != null;

  @BeforeAll
  static void prepare(@TempDir Path temp) throws Exception {
    sonarlintUserHome = temp.resolve("home");
    fakeTypeScriptProjectPath = temp.resolve("ts");

    var packagejson = fakeTypeScriptProjectPath.resolve("package.json");
    FileUtils.write(packagejson.toFile(), "{"
      + "\"devDependencies\": {\n" +
      "    \"typescript\": \"2.6.1\"\n" +
      "  }"
      + "}", StandardCharsets.UTF_8);
    var pb = new ProcessBuilder("npm" + (SystemUtils.IS_OS_WINDOWS ? ".cmd" : ""), "install")
      .directory(fakeTypeScriptProjectPath.toFile())
      .inheritIO();
    var process = pb.start();
    if (process.waitFor() != 0) {
      fail("Unable to run npm install");
    }

    Map<String, String> extraProperties = new HashMap<>();
    extraProperties.put("sonar.typescript.internal.typescriptLocation", fakeTypeScriptProjectPath.resolve("node_modules").toString());
    // See test sonarjs_should_honor_global_and_analysis_level_properties
    extraProperties.put("sonar.javascript.globals", "GLOBAL1");

    var nodeJsHelper = new NodeJsHelper();
    nodeJsHelper.detect(null);

    var configBuilder = StandaloneGlobalConfiguration.builder()
      .addPlugin(PluginLocator.getJavaScriptPluginPath())
      .addPlugin(PluginLocator.getJavaPluginPath())
      .addPlugin(PluginLocator.getPhpPluginPath())
      .addPlugin(PluginLocator.getPythonPluginPath())
      .addPlugin(PluginLocator.getXmlPluginPath())
      .addEnabledLanguages(Language.JS, Language.JAVA, Language.PHP, Language.PYTHON, Language.TS, Language.C, Language.YAML, Language.XML)
      .setSonarLintUserHome(sonarlintUserHome)
      .setNodeJs(nodeJsHelper.getNodeJsPath(), nodeJsHelper.getNodeJsVersion())
      .setExtraProperties(extraProperties);

    if (COMMERCIAL_ENABLED) {
      configBuilder.addPlugin(PluginLocator.getCppPluginPath());
    }
    sonarlint = new StandaloneSonarLintEngineImpl(configBuilder.build());
  }

  @AfterAll
  static void stop() throws IOException {
    sonarlint.stop();
  }

  @BeforeEach
  void prepareBasedir(@TempDir Path temp) throws Exception {
    baseDir = Files.createTempDirectory(temp, "baseDir").toFile();
  }

  @Test
  void simpleJava() throws Exception {
    var inputFile = prepareInputFile(A_JAVA_FILE_PATH,
      "public class Foo {\n"
        + "  public void foo() {\n"
        + "    int x;\n"
        + "    System.out.println(\"Foo\");\n"
        + "    // TODO full line issue\n"
        + "  }\n"
        + "}",
      false);

    final List<Issue> issues = new ArrayList<>();
    sonarlint.analyze(StandaloneAnalysisConfiguration.builder()
      .setBaseDir(baseDir.toPath())
      .addInputFile(inputFile)
      .build(), issues::add,
      null, null);

    assertThat(issues).extracting(Issue::getRuleKey, Issue::getStartLine, Issue::getStartLineOffset, Issue::getEndLine, Issue::getEndLineOffset,
      i -> i.getInputFile().relativePath(), Issue::getSeverity).containsOnly(
        tuple("java:S1220", null, null, null, null, A_JAVA_FILE_PATH, IssueSeverity.MINOR),
        tuple("java:S1481", 3, 8, 3, 9, A_JAVA_FILE_PATH, IssueSeverity.MINOR),
        tuple("java:S106", 4, 4, 4, 14, A_JAVA_FILE_PATH, IssueSeverity.MAJOR),
        tuple("java:S1135", 5, 0, 5, 27, A_JAVA_FILE_PATH, IssueSeverity.INFO));
  }

  private ClientInputFile prepareInputFile(String relativePath, String content, final boolean isTest, Charset encoding, @Nullable Language language) throws IOException {
    final var file = new File(baseDir, relativePath);
    FileUtils.write(file, content, encoding);
    return new OnDiskTestClientInputFile(file.toPath(), relativePath, isTest, encoding, language);
  }

  private ClientInputFile prepareInputFile(String relativePath, String content, final boolean isTest) throws IOException {
    return prepareInputFile(relativePath, content, isTest, StandardCharsets.UTF_8, null);
  }

}
