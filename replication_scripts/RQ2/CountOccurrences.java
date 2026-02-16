import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class CountOccurrences {
	
	static Set<String> non = new LinkedHashSet<>(Arrays.asList(
			"java:S1135",
			"java:S5993",
			"java:S112",
			"java:S3740",
			"java:S2189",
			"java:S3398",
			"java:S1171",
			"java:S1172",
			"java:S2142",
			"java:S1075",
			"java:S1854",
			"java:S2129",
			"java:S3626",
			"java:S2589",
			"java:S2184",
			"java:S1610",
			"java:S899",
			"java:S1130",
			"java:S108",
			"java:S1858",
			"java:S1186",
			"java:S1123",
			"java:S1133",
			"java:S1170",
			"java:S128",
			"java:S1134",
			"java:S2201",
			"java:S2583",
			"java:S3516",
			"java:S107",
			"java:S2273",
			"java:S1210",
			"java:S1488",
			"java:S4276",
			"java:S1118",
			"java:S1874",
			"java:S3077",
			"java:S2975",
			"java:S1182",
			"java:S6035",
			"java:S1104",
			"java:S1319",
			"java:S1191",
			"java:S1845",
			"java:S2692",
			"java:S5361",
			"java:S2696",
			"java:S2160",
			"java:S131",
			"java:S2629",
			"java:S5998",
			"java:S4042",
			"java:S1596",
			"java:S115",
			"java:S2886",
			"java:S2864",
			"java:S2225",
			"java:S1481",
			"java:S1149",
			"java:S3252",
			"java:S5413",
			"java:S2276",
			"java:S1068",
			"java:S1948",
			"java:S1214",
			"java:S3010",
			"java:S5843",
			"java:S1444",
			"java:S5411",
			"java:S4274",
			"java:S2062",
			"java:S2178",
			"java:S2925",
			"java:S4973",
			"java:S1452",
			"java:S5164",
			"java:S2112",
			"java:S3457",
			"java:S1163",
			"java:S1143",
			"java:S4719",
			"java:S2095",
			"java:S5869",
			"java:S6395",
			"java:S1643",
			"java:S2259",
			"java:S1157",
			"java:S1181",
			"java:S3014",
			"java:S3518",
			"java:S3011",
			"java:S1220",
			"java:S1598",
			"java:S4165",
			"java:S2786",
			"java:S4144",
			"java:S3346",
			"java:S5842",
			"java:S3864",
			"java:S1113",
			"java:S4968",
			"java:S2130",
			"java:S2139",
			"java:S1201",
			"java:S1193",
			"java:S2676",
			"java:S5527",
			"java:S1872",
			"java:S3416",
			"java:S1165",
			"java:S3078",
			"java:S3599",
			"java:S1150"
			
	));
	
	static Set<String> yes = new LinkedHashSet<>(Arrays.asList(
	"java:S1124",
	"java:S1141",
	"java:S1192",
	"java:S1066",
	"java:S3776",
	"java:S1197",
	"java:S125",
	"java:S1155",
	"java:S1117",
	"java:S1450",
	"java:S1604",
	"java:S120",
	"java:S2093",
	"java:S117",
	"java:S1602",
	"java:S1611",
	"java:S135",
	"java:S1301",
	"java:S100",
	"java:S1612",
	"java:S1144",
	"java:S106",
	"java:S1659",
	"java:S2293",
	"java:S1199",
	"java:S116",
	"java:S4201",
	"java:S3358",
	"java:S3008",
	"java:S1125",
	"java:S1126",
	"java:S127",
	"java:S1116",
	"java:S2147",
	"java:S1871",
	"java:S3878",
	"java:S1161",
	"java:S6213",
	"java:S1700",
	"java:S1121",
	"java:S3824",
	"java:S6353",
	"java:S1153",
	"java:S3012",
	"java:S1119",
	"java:S5261",
	"java:S119",
	"java:S1940",
	"java:S1905",
	"java:S3972",
	"java:S1264"
	));

	
	


	public static void main(String[] args) throws Exception {
		Map<String,Integer> quantosAntes = new HashMap();
		Map<String,Integer> quantasInstanciasAntes = new HashMap();
		
		Map<String,Integer> quantosDepois = new HashMap();
		Map<String,Integer> quantasInstanciasDepois = new HashMap();
		
		Map<String,Integer> quantosSobraramAntes = new HashMap();
		Map<String,Integer> quantosSobraramDepois = new HashMap();
		Map<String,Integer> quantosPermaneceramIgual = new HashMap();
		
		int quantosSameRules = 0;
		
		System.out.println("Sonar Recomendou o readability improvement?");
		//System.out.println("Code readability Improvements sugeridos pelo Sonar antes do commit");
		//System.out.println("Code readability Improvements sugeridos pelo Sonar depois do commit");
		File rootDir = new File("datasets/fileTemp");
		File dirs[] = rootDir.listFiles();
		for (int i = 2;i<= dirs.length+1;i++) {
			File dir = getDir(i,dirs);
			String name = dir.getName();
			//System.out.println(name);
			if (dir.listFiles().length == 0) {
				System.out.println("no");
				continue;
			}
			Set<String> rulesBefore = null;
			Set<String> rulesAfter = null;
			for (File file: dir.listFiles()) {				
				if (file.getName().equals("sonarLintAnalysis_before.csv")) {
					rulesBefore = getViolations(file);
					quantasInstanciasAntes = getViolationsInstancias(quantasInstanciasAntes,file);
				}
				
				if (file.getName().equals("sonarLintAnalysis_after.csv")) {
					rulesAfter = getViolations(file);
					quantasInstanciasDepois = getViolationsInstancias(quantasInstanciasDepois,file);
				}				
			} 			
			//firstColumn(rulesBefore,rulesAfter);
			//secondColumn(rulesBefore);
			//secondColumn(rulesAfter);
			//rulesNotFinded(name,rulesBefore,rulesAfter);
			
			addRules(quantosAntes,rulesBefore);
			addRules(quantosDepois,rulesAfter);
			
			if (rulesBefore.equals(rulesAfter)) {
				quantosSameRules++;
			}
			
			addRules(quantosSobraramAntes,getDiff(rulesBefore,rulesAfter));
			addRules(quantosSobraramDepois,getDiff(rulesAfter,rulesBefore));
			addRules(quantosPermaneceramIgual,igual(rulesAfter,rulesBefore));
		}
		
		System.out.println("Quantidade total before");
		System.out.println(getOrdenado(quantosAntes));
		
		System.out.println("Quantidade total after");
		System.out.println(getOrdenado(quantosDepois));
		
		System.out.println("Quantidade instancias before");
		System.out.println(getOrdenado(quantasInstanciasAntes));
		
		System.out.println("Quantidade instancias after");
		System.out.println(getOrdenado(quantasInstanciasDepois));
		
		
		
		System.out.println("Quantidade sobraram antes");
		System.out.println(getOrdenado(quantosSobraramAntes));
		
		System.out.println("Quantidade sobraram depois");
		System.out.println(getOrdenado(quantosSobraramDepois));
		
		System.out.println("Quantidade permaneceram igual");
		System.out.println(getOrdenado(quantosPermaneceramIgual));
		
		System.out.println("Quantos same rules");
		System.out.println(quantosSameRules);
	}
	


	private static Set<String> igual(Set<String> rules1, Set<String> rules2) {
		Set<String> rules = new LinkedHashSet();
		for (String rule: rules1) {
			if (rules2.contains(rule)) {
				rules.add(rule);
			}
		}
		return rules;
	}

	private static Set<String> getDiff(Set<String> rules1, Set<String> rules2) {
		Set<String> rules = new LinkedHashSet();
		for (String rule: rules1) {
			if (!rules2.contains(rule)) {
				rules.add(rule);
			}
		}
		return rules;
	}

	public static Map<String,Integer> getOrdenado(Map<String,Integer> mapa) {
		return mapa.entrySet()
			    .stream()
			    .sorted(Map.Entry.comparingByValue(Comparator.reverseOrder()))
			    .collect(Collectors.toMap(
			        Map.Entry::getKey,
			        Map.Entry::getValue,
			        (oldValue, newValue) -> oldValue, LinkedHashMap::new));
	}



	private static void addRules(Map<String, Integer> quantos, Set<String> rules) {
		for(String rule: rules) {
			if (quantos.containsKey(rule)) {
				int valor = quantos.get(rule);
				valor++;
				quantos.put(rule,valor);
			} else {
				quantos.put(rule,1);
			}
		}
		
	}



	private static void rulesNotFinded(String name, Set<String> rulesBefore, Set<String> rulesAfter) {
		String texto = name+" - ";
		for (String rule:rulesBefore) {
			if (!yes.contains(rule) && !non.contains(rule)) {
				texto += rule+",";
			}
		}
		for (String rule:rulesAfter) {
			if (!yes.contains(rule) && !non.contains(rule)) {
				texto += rule+",";
			}
		}
		System.out.println(texto);
		
	}



	private static void secondColumn(Set<String> rulesBefore) {
		String texto = "";
		for (String rule:rulesBefore) {
			if (yes.contains(rule)) {
				texto += rule+",";
			}
		}
		System.out.println(texto);
	}



	private static void firstColumn(Set<String> rulesBefore, Set<String> rulesAfter) {
		if (rulesBefore.isEmpty() && rulesAfter.isEmpty()) {
			System.out.println("no");
		} else {
			System.out.println("");
		}
	}



	private static File getDir(int i, File[] dirs) {
		for (File dir: dirs) {
			if (dir.getName().equals(i+"")) {
				return dir;
			}
		}
		return null;
	}



	private static Set<String> getViolations(File file) throws Exception {
		Set<String> violations = new LinkedHashSet<>();
	
		BufferedReader br = new BufferedReader(new FileReader(file));
		while (br.ready()) {
			String line = br.readLine();
			String rule = line.split(",")[0];
			if (rule.startsWith("java:")) {
				if (!non.contains(rule)) {
					violations.add(rule);	
				}				
			}
		}
		
		return violations;
	}
	
	private static Map<String, Integer> getViolationsInstancias(Map<String, Integer> violations,File file)throws Exception {		
		BufferedReader br = new BufferedReader(new FileReader(file));
		while (br.ready()) {
			String line = br.readLine();
			String rule = line.split(",")[0];
			if (rule.startsWith("java:")) {
				if (!non.contains(rule)) {
					if (violations.containsKey(rule)) {
						int valor = violations.get(rule);
						valor++;
						violations.put(rule,valor);
					} else {
						violations.put(rule,1);
					}
				}				
			}
		}
		
		return violations;
	}
}