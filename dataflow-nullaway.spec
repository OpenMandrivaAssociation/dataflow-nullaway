Name:		dataflow-nullaway
Version:	4.4.0
Release:	1
Summary:	Checker Framework dataflow shaded for NullAway
Group:		Development/Java
License:	GPL-2.0-only WITH Classpath-exception-2.0
URL:		https://checkerframework.org/
# Checker Framework 4.4.0 dataflow and javacutil sources. No Gradle wrapper and no class files.
Source0:	dataflow-nullaway-%{version}.tar.gz
# Tag checker-framework-4.0.0, dataflow and javacutil main sources only.
Source1:	dataflow-nullaway-4.0.0.tar.gz
# Pure.Kind moved off checker-qual 4.4.0. Applied only to the 4.0.0 side tree.
Patch0:		dataflow-nullaway-4.0.0-system-libs.patch

%{!?plume_jar:%global plume_jar %{_javadir}/plume-util.jar}
%{!?plume_old_jar:%global plume_old_jar %{_javadir}/plume-util-1.8.1.jar}
%{!?reflection_jar:%global reflection_jar %{_javadir}/reflection-util.jar}
%{!?reflection_old_jar:%global reflection_old_jar %{_javadir}/reflection-util-1.0.6.jar}
%{!?hashmap_jar:%global hashmap_jar %{_javadir}/hashmap-util.jar}
%{!?hashmap_old_jar:%global hashmap_old_jar %{_javadir}/hashmap-util-0.0.1.jar}
%{!?javacparse_jar:%global javacparse_jar %{_javadir}/javac-parse.jar}
%{!?javacparse_old_jar:%global javacparse_old_jar %{_javadir}/javac-parse-0.9.0.jar}

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(org.checkerframework:checker-qual) = 4.4.0
BuildRequires:	mvn(org.plumelib:plume-util) = 2.0.0
BuildRequires:	mvn(org.plumelib:plume-util) = 1.8.1
BuildRequires:	mvn(org.plumelib:reflection-util) = 2.0.0
BuildRequires:	mvn(org.plumelib:reflection-util) = 1.0.6
BuildRequires:	mvn(org.plumelib:hashmap-util) = 2.0.0
BuildRequires:	mvn(org.plumelib:hashmap-util) = 0.0.1
BuildRequires:	mvn(org.plumelib:javac-parse) = 1.0.0
BuildRequires:	mvn(org.plumelib:javac-parse) = 0.9.0
BuildRequires:	mvn(com.google.guava:guava) = 33.6.0-jre
Requires:	mvn(org.checkerframework:checker-qual) = 4.4.0
Requires:	mvn(org.plumelib:plume-util) = 2.0.0
Requires:	mvn(org.plumelib:plume-util) = 1.8.1
Requires:	mvn(org.plumelib:reflection-util) = 2.0.0
Requires:	mvn(org.plumelib:reflection-util) = 1.0.6
Requires:	mvn(org.plumelib:hashmap-util) = 2.0.0
Requires:	mvn(org.plumelib:hashmap-util) = 0.0.1
Requires:	mvn(org.plumelib:javac-parse) = 1.0.0
Requires:	mvn(org.plumelib:javac-parse) = 0.9.0
Requires:	mvn(com.google.guava:guava) = 33.6.0-jre

%description
org.checkerframework:dataflow-nullaway %{version}. NullAway calls the
Checker Framework dataflow and javacutil packages after they have been
renamed under org.checkerframework.nullaway. The unversioned jar is that
rename, built with javac from the Checker Framework 4.4.0 sources.
4.0.0 stays as a side jar so an exact require for that version still
resolves. org.checkerframework.dataflow.qual stays in checker-qual.
plume-util, reflection-util, hashmap-util, javac-parse, and guava are
the system jars, not copies shaded into this one. 4.4.0 already contains
PurityUtils and PurityKind. The Pure.Kind adaptation is applied only to
the 4.0.0 side jar.

%prep
%autosetup -N -n dataflow-nullaway-%{version}
tar -C %{_builddir} -xzf %{SOURCE1}
patch -d %{_builddir}/dataflow-nullaway-4.0.0 -p1 -i %{_sourcedir}/dataflow-nullaway-4.0.0-system-libs.patch
for dir in "%{_builddir}/dataflow-nullaway-%{version}" "%{_builddir}/dataflow-nullaway-4.0.0"; do
	find "$dir" -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > "$dir/binaries.list"
	find "$dir" -type d -name '*.jar' -print >> "$dir/binaries.list"
	if [ -s "$dir/binaries.list" ]; then
		cat "$dir/binaries.list"
		exit 1
	fi
done

%build
set -eo pipefail
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
build_tree() {
	root=$1
	expect=$2
	cp=$3
	ver=$4
	cd "$root"
	find dataflow/src/main/java javacutil/src/main/java -name '*.java' > sources.list
	test "$(wc -l < sources.list)" -eq "$expect"
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
	/bin/mv dataflow/src/main/java/org/checkerframework/dataflow dataflow/src/main/java/org/checkerframework/nullaway/dataflow
	/bin/mv javacutil/src/main/java/org/checkerframework/javacutil javacutil/src/main/java/org/checkerframework/nullaway/javacutil
	find dataflow/src/main/java javacutil/src/main/java -name '*.java' > sources.list
	test "$(wc -l < sources.list)" -eq "$expect"
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
	echo "$cp" >> javac.args
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
	if [ "$ver" = "4.4.0" ]; then
		cat > dataflow-nullaway.pom << 'END'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.checkerframework</groupId>
  <artifactId>dataflow-nullaway</artifactId>
  <version>4.4.0</version>
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
      <version>2.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.plumelib</groupId>
      <artifactId>reflection-util</artifactId>
      <version>2.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.plumelib</groupId>
      <artifactId>hashmap-util</artifactId>
      <version>2.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.plumelib</groupId>
      <artifactId>javac-parse</artifactId>
      <version>1.0.0</version>
    </dependency>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>33.6.0-jre</version>
    </dependency>
  </dependencies>
</project>
END
		grep -F -q '<version>4.4.0</version>' dataflow-nullaway.pom
	else
		cat > dataflow-nullaway.pom << 'END'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.checkerframework</groupId>
  <artifactId>dataflow-nullaway</artifactId>
  <version>4.0.0</version>
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
      <artifactId>hashmap-util</artifactId>
      <version>0.0.1</version>
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
		grep -F -q '<version>4.0.0</version>' dataflow-nullaway.pom
	fi
}
oldcp="%{plume_old_jar}:%{reflection_old_jar}:%{hashmap_old_jar}:%{_javadir}/checker-qual.jar:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{javacparse_old_jar}"
newcp="%{plume_jar}:%{reflection_jar}:%{hashmap_jar}:%{_javadir}/checker-qual.jar:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{javacparse_jar}"
build_tree "%{_builddir}/dataflow-nullaway-4.0.0" 206 "$oldcp" 4.0.0
build_tree "%{_builddir}/dataflow-nullaway-%{version}" 208 "$newcp" 4.4.0

%install
set -eo pipefail
old="%{_builddir}/dataflow-nullaway-4.0.0"
sysjar install --buildroot %{buildroot} \
	--artifact "${old}/dataflow-nullaway.pom:${old}/dataflow-nullaway.jar" \
	--file-name dataflow-nullaway-4.0.0 \
	--filelist .mfiles-old
index="%{buildroot}/usr/share/sysjar/index/org.checkerframework/dataflow-nullaway.sysjar"
test -f "$index"
/bin/mv "$index" "%{buildroot}/usr/share/sysjar/index/org.checkerframework/dataflow-nullaway-4.0.0.sysjar"
sed -i 's|/usr/share/sysjar/index/org\.checkerframework/dataflow-nullaway\.sysjar|/usr/share/sysjar/index/org.checkerframework/dataflow-nullaway-4.0.0.sysjar|' .mfiles-old
idx="%{buildroot}/usr/share/sysjar/index/org.checkerframework/dataflow-nullaway-4.0.0.sysjar"
grep -F -q '"version": "4.0.0"' "$idx"
grep -F -q '"artifactId": "dataflow-nullaway"' "$idx"
new="%{_builddir}/dataflow-nullaway-%{version}"
sysjar install --buildroot %{buildroot} \
	--artifact "${new}/dataflow-nullaway.pom:${new}/dataflow-nullaway.jar" \
	--file-name dataflow-nullaway \
	--filelist .mfiles-new
idxn="%{buildroot}/usr/share/sysjar/index/org.checkerframework/dataflow-nullaway.sysjar"
grep -F -q '"version": "4.4.0"' "$idxn"
grep -F -q '"artifactId": "dataflow-nullaway"' "$idxn"
test -s %{buildroot}%{_javadir}/dataflow-nullaway-4.0.0.jar
test -s %{buildroot}%{_javadir}/dataflow-nullaway.jar
: > .mfiles
for list in .mfiles-old .mfiles-new
do
	while IFS= read -r line; do
		grep -qxF -- "$line" .mfiles || printf '%%s\n' "$line" >> .mfiles
	done < "$list"
done
grep -F -q '/dataflow-nullaway.jar' .mfiles
grep -F -q '/dataflow-nullaway-4.0.0.jar' .mfiles

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
		int index = JavaExpressionParseUtil.parameterIndex(args[2]);
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
		System.out.println("dataflow_na_ok " + args[1] + " " + nodes.size() + " " + returns + " " + index);
		if (nodes.size() != 5 || returns != 2) {
			throw new AssertionError(nodes.size() + " " + returns);
		}
	}
}
EOF
run_check() {
	label=$1
	df=$2
	extra=$3
	outdir=$4
	base="%{_javadir}/checker-qual.jar:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar"
	cp="${df}:${extra}:${base}"
	mkdir -p "$outdir"
	: > "$outdir/check.args"
	echo -encoding >> "$outdir/check.args"
	echo UTF-8 >> "$outdir/check.args"
	echo -proc:none >> "$outdir/check.args"
	echo -cp >> "$outdir/check.args"
	echo "$cp" >> "$outdir/check.args"
	for p in api code comp file jvm main model parser processing resources tree util; do
		echo "--add-exports=jdk.compiler/com.sun.tools.javac.${p}=ALL-UNNAMED" >> "$outdir/check.args"
	done
	echo -d >> "$outdir/check.args"
	echo "$outdir" >> "$outdir/check.args"
	echo check/CheckDataflow.java >> "$outdir/check.args"
	javac @"$outdir/check.args"
	: > "$outdir/java.args"
	for p in api code comp file jvm main model parser processing resources tree util; do
		echo "--add-exports=jdk.compiler/com.sun.tools.javac.${p}=ALL-UNNAMED" >> "$outdir/java.args"
		echo "--add-opens=jdk.compiler/com.sun.tools.javac.${p}=ALL-UNNAMED" >> "$outdir/java.args"
	done
	echo -cp >> "$outdir/java.args"
	echo "${outdir}:${cp}" >> "$outdir/java.args"
	token=$(printf '\0432')
	java @"$outdir/java.args" CheckDataflow check/Sample.java "$label" "$token" > "$outdir/out.txt"
	cat "$outdir/out.txt"
	grep -F -q "dataflow_na_ok ${label} 5 2 2" "$outdir/out.txt"
}
run_check 4.4.0 %{buildroot}%{_javadir}/dataflow-nullaway.jar "%{plume_jar}:%{reflection_jar}:%{hashmap_jar}:%{javacparse_jar}" check-new
run_check 4.0.0 %{buildroot}%{_javadir}/dataflow-nullaway-4.0.0.jar "%{plume_old_jar}:%{reflection_old_jar}:%{hashmap_old_jar}:%{javacparse_old_jar}" check-old

%files -f .mfiles
%license LICENSE.txt
