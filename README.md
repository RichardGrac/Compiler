# Compiler
<p>Compiler guided in the Tiny Compiler by Louden from the Book: 
   	<i>UNED Construccion de compiladores principios y practica - Kenneth C Louden -International _Thomson Editores - 2004</i>.
 
 If you want to run the Compiler, there are two ways. With GUI or without GUI.</p>
 # <h3>With GUI:</h3>
 <p>Download the 'Compiler GUI' of my partner: https://github.com/Joshua195/IDE_Compilador 
 
 Then you have to change the <b>'PATH'</b> var whose is related by the Folder with files in Python corresponding to the compiler.
 
 It is in Controller.java:</p>
 
 <code>43: public static final String PATH = "C:\\Users\\Richa\\PycharmProjects\\Compiler\\";</code>
 
 <p>And Run the Compiler since the 'IDE'.</p>

 # <h3>Without GUI:</h3>
 <p>You have to comment and discomment some lines in some files corresponding to the use of the IDE:</p>
 <p><i> [<b>D</b>]iscomment [<b>C</b>]omment </i></p>
 <p>
 <code><b> Lexico.py</b> [<b>D</b>] 76 [<b>C</b>] 79, 80</code>

 <code><b> Sintactico.py</b> [<b>D</b>] 42 [<b>C</b>] 38, 39</code>

 <code><b> Gramatical.py</b> [<b>D</b>] 562, 563 [<b>C</b>] 567, 568</code>

 <code><b> GenCodigo.py</b> [<b>D</b>] 425, 426, 433, 434 [<b>C</b>] 429, 430, 437, 438</code>
</p>
 <p>And Run the files one by one since your Python IDE or Console: [Lexico.py, Sintactico.py, Gramatical.py] or [Main.py], GenCodigo.py and TM.py.</p>
