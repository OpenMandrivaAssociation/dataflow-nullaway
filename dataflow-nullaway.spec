Name:		dataflow-nullaway
Version:	4.0.0
Release:	1
Summary:	Checker Framework dataflow shaded for NullAway
Group:		Development/Java
License:	GPL-2.0-only WITH Classpath-exception-2.0
URL:		https://checkerframework.org/
# Tag checker-framework-4.0.0, dataflow and javacutil main sources only.
# The Checker Framework Gradle wrapper and prebuilt jars are not in this archive.
Source0:	dataflow-nullaway-%{version}.tar.gz
# Use system plume-util, and keep Pure.Kind off checker-qual 4.4.0.
Patch0:		dataflow-nullaway-4.0.0-system-libs.patch

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(org.checkerframework:checker-qual) = 4.4.0
BuildRequires:	mvn(org.plumelib:plume-util) = 1.8.1
BuildRequires:	mvn(org.plumelib:reflection-util) = 1.0.6
BuildRequires:	mvn(org.plumelib:hashmap-util) = 0.0.1
BuildRequires:	mvn(com.google.guava:guava) = 33.6.0-jre
BuildRequires:	mvn(org.plumelib:javac-parse) = 0.9.0
Requires:	mvn(org.checkerframework:checker-qual) = 4.4.0
Requires:	mvn(org.plumelib:plume-util) = 1.8.1
Requires:	mvn(org.plumelib:reflection-util) = 1.0.6
Requires:	mvn(com.google.guava:guava) = 33.6.0-jre
Requires:	mvn(org.plumelib:javac-parse) = 0.9.0

%description
org.checkerframework:dataflow-nullaway %{version}. NullAway 0.13.7 calls
the Checker Framework dataflow and javacutil packages after they have been
renamed under org.checkerframework.nullaway. This jar is that rename, built
with javac from the 4.0.0 sources. org.checkerframework.dataflow.qual and
org.checkerframework.checker stay in checker-qual. plume-util and guava are
the system jars, not copies shaded into this one.

%prep
%autosetup -n dataflow-nullaway-%{version} -p1
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
find . -type d -name '*.jar' -print >> binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
find dataflow/src/main/java javacutil/src/main/java -name '*.java' > sources.list
test "$(wc -l < sources.list)" -eq 206
while IFS= read -r src; do
	sed -i \
		-e 's/org\.checkerframework\.dataflow\.qual/KEEP_DATAFLOW_QUAL/g' \
		-e 's/org\.checkerframework\.javacutil/org.checkerframework.nullaway.javacutil/g' \
		-e 's/org\.checkerframework\.dataflow/org.checkerframework.nullaway.dataflow/g' \
		-e 's/KEEP_DATAFLOW_QUAL/org.checkerframework.dataflow.qual/g' \
		"$src"
done < sources.list
mkdir -p dataflow/src/main/java/org/checkerframework/nullaway
mkdir -p javacutil/src/main/java/org/checkerframework/nullaway
mv dataflow/src/main/java/org/checkerframework/dataflow dataflow/src/main/java/org/checkerframework/nullaway/dataflow
mv javacutil/src/main/java/org/checkerframework/javacutil javacutil/src/main/java/org/checkerframework/nullaway/javacutil
find dataflow/src/main/java javacutil/src/main/java -name '*.java' > sources.list
test "$(wc -l < sources.list)" -eq 206
if grep -R -l 'KEEP_DATAFLOW_QUAL' --include='*.java' dataflow javacutil; then
	exit 1
fi
if grep -R -n 'org\.checkerframework\.javacutil' --include='*.java' dataflow javacutil | grep -v 'org\.checkerframework\.nullaway\.javacutil'; then
	exit 1
fi
if grep -R -n 'org\.checkerframework\.dataflow' --include='*.java' dataflow javacutil | grep -v 'org\.checkerframework\.dataflow\.qual' | grep -v 'org\.checkerframework\.nullaway\.dataflow'; then
	exit 1
fi
test -f dataflow/src/main/java/org/checkerframework/nullaway/dataflow/cfg/builder/CFGBuilder.java
mkdir -p classes
: > javac.args
echo -encoding >> javac.args
echo UTF-8 >> javac.args
echo -proc:none >> javac.args
echo -Xlint:-options,-removal,-processing,-this-escape >> javac.args
echo -cp >> javac.args
echo "%{_javadir}/checker-qual.jar:%{_javadir}/plume-util.jar:%{_javadir}/reflection-util.jar:%{_javadir}/hashmap-util.jar:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{_javadir}/javac-parse.jar" >> javac.args
for p in api code comp file jvm main model parser processing resources tree util; do
	echo "--add-exports=jdk.compiler/com.sun.tools.javac.${p}=ALL-UNNAMED" >> javac.args
done
echo -d >> javac.args
echo classes >> javac.args
cat sources.list >> javac.args
javac @javac.args
echo 'Automatic-Module-Name: org.checkerframework.nullaway' > dataflow-nullaway.mf
jar cfm dataflow-nullaway.jar dataflow-nullaway.mf -C classes .
jar i dataflow-nullaway.jar
if jar tf dataflow-nullaway.jar | grep -E '\.(java|jar|so|node|wasm)$'; then
	exit 1
fi
feature=$(java -XshowSettings:properties -version 2>&1 | awk -F= '/java.specification.version/{gsub(/ /,"",$2); print $2}')
major=$((feature + 44))
javap -v -classpath dataflow-nullaway.jar org.checkerframework.nullaway.dataflow.cfg.builder.CFGBuilder | grep -F -q "major version: ${major}"
desc=$(jar --describe-module --file dataflow-nullaway.jar)
printf '%s\n' "$desc" | grep -F -q 'org.checkerframework.nullaway'
if printf '%s\n' "$desc" | grep -F -q 'Unable'; then
	exit 1
fi

cat > dataflow-nullaway.pom << END
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.checkerframework</groupId>
  <artifactId>dataflow-nullaway</artifactId>
  <version>%{version}</version>
  <name>dataflow-nullaway</name>
  <description>Checker Framework dataflow and javacutil renamed for NullAway.</description>
  <url>https://checkerframework.org/</url>
  <licenses>
    <license>
      <name>GPL-2.0-only WITH Classpath-exception-2.0</name>
      <url>https://www.gnu.org/licenses/old-licenses/gpl-2.0.html</url>
      <distribution>repo</distribution>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>org.checkerframework</groupId>
      <artifactId>checker-qual</artifactId>
      <version>4.4.0</version>
    </dependency>
    <dependency>
      <groupId>org.plumelib</groupId>
      <artifactId>plume-util</artifactId>
      <version>1.8.1</version>
    </dependency>
    <dependency>
      <groupId>org.plumelib</groupId>
      <artifactId>reflection-util</artifactId>
      <version>1.0.6</version>
    </dependency>
    <dependency>
      <groupId>org.plumelib</groupId>
      <artifactId>javac-parse</artifactId>
      <version>0.9.0</version>
    </dependency>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>33.6.0-jre</version>
    </dependency>
  </dependencies>
</project>
END

%install
sysjar install --buildroot %{buildroot} \
	--artifact dataflow-nullaway.pom:dataflow-nullaway.jar \
	--file-name dataflow-nullaway \
	--filelist .mfiles

%check
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
mkdir -p check
cat > check/Sample.java << 'EOF'
public class Sample {
	int branch(boolean flag) {
		if (flag) {
			return 1;
		} else {
			return 0;
		}
	}
}
EOF
cat > check/CheckDataflow.java << 'EOF'
import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.Tree;
import com.sun.source.util.JavacTask;
import com.sun.tools.javac.api.BasicJavacTask;
import com.sun.tools.javac.processing.JavacProcessingEnvironment;
import com.sun.tools.javac.util.Context;
import java.nio.file.Path;
import java.util.List;
import javax.annotation.processing.ProcessingEnvironment;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;
import org.checkerframework.nullaway.dataflow.cfg.ControlFlowGraph;
import org.checkerframework.nullaway.dataflow.cfg.builder.CFGBuilder;
import org.checkerframework.nullaway.dataflow.cfg.node.Node;
import org.checkerframework.nullaway.dataflow.expression.JavaExpressionParseUtil;

public class CheckDataflow {
	public static void main(String[] args) throws Exception {
		int index = JavaExpressionParseUtil.parameterIndex("#2");
		if (index != 2) {
			throw new AssertionError(index);
		}
		JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
		StandardJavaFileManager fm = compiler.getStandardFileManager(null, null, null);
		Iterable<? extends JavaFileObject> files = fm.getJavaFileObjects(Path.of(args[0]));
		JavacTask task = (JavacTask) compiler.getTask(null, fm, null, List.of("--release", "8"), null, files);
		Iterable<? extends CompilationUnitTree> units = task.parse();
		task.analyze();
		CompilationUnitTree root = units.iterator().next();
		ClassTree cls = (ClassTree) root.getTypeDecls().get(0);
		MethodTree method = null;
		for (Tree member : cls.getMembers()) {
			if (member instanceof MethodTree) {
				MethodTree mt = (MethodTree) member;
				if (mt.getName().contentEquals("branch")) {
					method = mt;
				}
			}
		}
		if (method == null) {
			throw new AssertionError("no branch");
		}
		Context ctx = ((BasicJavacTask) task).getContext();
		ProcessingEnvironment env = JavacProcessingEnvironment.instance(ctx);
		ControlFlowGraph cfg = CFGBuilder.build(root, method, cls, env);
		List<Node> nodes = cfg.getAllNodes();
		int returns = 0;
		for (Node n : nodes) {
			if (n.getClass().getSimpleName().equals("ReturnNode")) {
				returns++;
			}
		}
		System.out.println("dataflow_na_ok " + nodes.size() + " " + returns + " " + index);
		if (nodes.size() < 2 || returns < 2) {
			throw new AssertionError("cfg too small");
		}
	}
}
EOF
JAR=%{buildroot}%{_javadir}/dataflow-nullaway.jar
test -s "$JAR"
CP="$JAR:%{_javadir}/checker-qual.jar:%{_javadir}/plume-util.jar:%{_javadir}/reflection-util.jar:%{_javadir}/hashmap-util.jar:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{_javadir}/javac-parse.jar"
: > check.args
echo -encoding >> check.args
echo UTF-8 >> check.args
echo -proc:none >> check.args
echo -cp >> check.args
echo "$CP" >> check.args
for p in api code comp file jvm main model parser processing resources tree util; do
	echo "--add-exports=jdk.compiler/com.sun.tools.javac.${p}=ALL-UNNAMED" >> check.args
done
echo -d >> check.args
echo check >> check.args
echo check/CheckDataflow.java >> check.args
javac @check.args
: > java.args
for p in api code comp file jvm main model parser processing resources tree util; do
	echo "--add-exports=jdk.compiler/com.sun.tools.javac.${p}=ALL-UNNAMED" >> java.args
	echo "--add-opens=jdk.compiler/com.sun.tools.javac.${p}=ALL-UNNAMED" >> java.args
done
echo -cp >> java.args
echo "check:$CP" >> java.args
echo CheckDataflow >> java.args
echo check/Sample.java >> java.args
java @java.args > check/out.txt
cat check/out.txt
grep -F -q 'dataflow_na_ok 5 2 2' check/out.txt

%files -f .mfiles
%license LICENSE.txt
