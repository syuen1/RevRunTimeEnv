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
1. Run the code forward (code.txt is the compiled SM code)
> py ./vmCUI.py code.txt f v
> mode 1:auto 2:select >> 1
> (vm runs without stopping)
> mode 1:auto 2:select >> 2
> (vm runs step by step)
label stack : lstack.txt  value stack : rstack.txt  final variable values: variable_region.txt
1. Invert the code
> py ./vm_CUI.py code.txt invcode.txt
1. Run the code backward
> py ./vmCUI.py invcode.txt
> mode 1:auto 2:select >> 

