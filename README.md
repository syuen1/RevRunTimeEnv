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
