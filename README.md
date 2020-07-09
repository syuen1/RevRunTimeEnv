# RevRunTimeEnv
Reversible Runtime Environment for Parallel Programs

vm.py: Stack machine by Python<br>
StackMachineSpec.pdf: Specification of the reversible stack machine<br>
(Corrected from the one submitted to RC2020)
<br>Example: Airline ticket example
<br>
### Running the translator
1. Compile the translator<br>
> `javacc Parser.jj`<br>
> `javac *.java`
2. Run the translator<br>
> `java -cp . Parser airline.txt`

### Run the compiled code
1. Run the code forward (code.txt is the compiled SM code)<br>
> py ./vmCUI.py code.txt f v<br>
> mode 1:auto 2:select >> 1<br>
> (vm runs without stopping)<br>
> mode 1:auto 2:select >> 2<br>
> (vm runs step by step)<br>
label stack : lstack.txt  value stack : rstack.txt  final variable values: variable_region.txt<br>
1. Invert the code<br>
> py ./vm_CUI.py code.txt invcode.txt<br>
1. Run the code backward<br>
> py ./vmCUI.py invcode.txt b v<br>
> mode 1:auto 2:select >> <br>

