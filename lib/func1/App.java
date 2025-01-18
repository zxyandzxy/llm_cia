package edu.sysu;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseProblemException;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ParserConfiguration;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;

public class App
{
    // Inheritance(IH)
    public String checkInheritance(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();

        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            // Parsing Ci and Cj files for CompilationUnit
            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            // Get all class or interface declarations in Cj
            for (ClassOrInterfaceDeclaration impactedClass : cj.findAll(ClassOrInterfaceDeclaration.class)) {
                // An inheritance relationship exists if Cj is a class and its parent class name matches any class name in Ci
                if (impactedClass.isClassOrInterfaceDeclaration()) {
                    for (com.github.javaparser.ast.type.ClassOrInterfaceType extendedType : impactedClass.getExtendedTypes()) {
                        Optional<ClassOrInterfaceDeclaration> parentClassInCi = ci.getClassByName(extendedType.getNameAsString());
                        if (parentClassInCi.isPresent()) {
                            result.append("Inheritance found: ").append(impactedClass.getName())
                                    .append(" extends ").append(parentClassInCi.get().getName()).append(",  ");
                        }
                    }
                }
            }

            return result.length() > 0 ? result.toString() : "";

        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Implementing Interface(II)
    public String checkInterfaceImplementation(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();

        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            for (ClassOrInterfaceDeclaration impactedClass : cj.findAll(ClassOrInterfaceDeclaration.class)) {
                // An interface realization relationship exists if Cj implements any interface in Ci
                for (com.github.javaparser.ast.type.ClassOrInterfaceType implementedType : impactedClass.getImplementedTypes()) {
                    Optional<ClassOrInterfaceDeclaration> interfaceInCi = ci.getInterfaceByName(implementedType.getNameAsString());
                    if (interfaceInCi.isPresent()) {
                        result.append("Interface Implementation found: ").append(impactedClass.getName())
                                .append(" implements ").append(interfaceInCi.get().getName()).append(",  ");
                    }
                }
            }

            return result.length() > 0 ? result.toString() : "";

        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Type-Casting (TC)
    public String checkTypeCasting(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            // Find all type conversion expressions in Ci
            ci.findAll(CastExpr.class).forEach(typeCastExpr -> {
                String castType = typeCastExpr.getType().toString();
                if (cj.getTypes().stream().anyMatch(t -> t.getNameAsString().equals(castType))) {
                    result.append("Type Casting found: ").append(typeCastExpr.toString()).append(",  ");
                }
            });

            return result.length() > 0 ? result.toString() : "";
        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Instanceof (IO)
    public String checkInstanceof(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            // Find all instanceof expressions in Ci
            ci.findAll(InstanceOfExpr.class).forEach(instanceOfExpr -> {
                String checkedType = instanceOfExpr.getType().toString();
                if (cj.getTypes().stream().anyMatch(t -> t.getNameAsString().equals(checkedType))) {
                    result.append("Instanceof found: ").append(instanceOfExpr.toString()).append(",  ");
                }
            });

            return result.length() > 0 ? result.toString() : "";
        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Return Type (RT)
    public String checkReturnType(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            // Find all method declarations in Ci and check their return types
            ci.findAll(MethodDeclaration.class).forEach(method -> {
                String returnType = method.getType().toString();
                if (cj.getTypes().stream().anyMatch(t -> t.getNameAsString().equals(returnType))) {
                    result.append("Return Type found: ").append(method.getName())
                            .append(" returns ").append(returnType).append(",  ");
                }
            });

            return result.length() > 0 ? result.toString() : "";
        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Exception Throws (ET)
    public String checkExceptionThrows(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            // Find all method declarations in Ci and check for exceptions thrown by them
            ci.findAll(MethodDeclaration.class).forEach(method -> {
                method.getThrownExceptions().forEach(thrownException -> {
                    if (cj.getTypes().stream().anyMatch(t -> t.getNameAsString().equals(thrownException.asString()))) {
                        result.append("Exception Throws found: ").append(method.getName())
                                .append(" throws ").append(thrownException).append(",  ");
                    }
                });
            });

            return result.length() > 0 ? result.toString() : "";
        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Method Member Variable Usage Variable (MMAUA)
    public String checkMMAUA(String ciFilePath, String cjFilePath) {
        /*
        A method of class Ci defines an instance cj of Cj, and then uses the instance cj of Cj in code (not calling a member variable of Cj through Cj, not calling a member method through Cj)
        public class Cj {
            public void doSomething() {
                // Do something...
            }
        }
        public class Ci {
            public void someMethod() {
                Cj cj = new Cj();
                System.out.println(cj); // Directly using the cj example
            }
        }
         */
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            // Get Cj class name
            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findAll(ClassOrInterfaceDeclaration.class).stream()
                    .filter(cjd -> !cjd.isInterface())
                    .findFirst();
            if (!cjClassOpt.isPresent()) return "";
            String cjClassName = cjClassOpt.get().getNameAsString();

            // Create an accessor to find a reference to Cj in Ci
            ciCU.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);
                    // Finding objects to create expressions
                    md.findAll(ObjectCreationExpr.class).forEach(oce -> {
                        if (oce.getType().toString().equals(cjClassName)) {
                            boolean usedDirectly = true;

                            // Check that the created object is used directly (not as part of a method call)
                            Node parent = oce.getParentNode().orElse(null);
                            while (parent != null && !(parent instanceof MethodDeclaration)) {
                                if (parent instanceof MethodCallExpr) {
                                    usedDirectly = false;
                                    break;
                                }
                                parent = parent.getParentNode().orElse(null);
                            }

                            // Verify that it is not used as an argument to a method call
                            if (usedDirectly) {
                                Optional<Expression> scope = oce.findFirst(Expression.class, expr ->
                                        expr instanceof MethodCallExpr && ((MethodCallExpr) expr).getScope().isPresent() &&
                                                ((MethodCallExpr) expr).getScope().get().equals(oce)
                                );
                                if (scope.isPresent()) {
                                    usedDirectly = false;
                                }
                            }

                            if (usedDirectly) {
                                couplingInfo.append("Coupling found in method ").append(md.getName())
                                        .append(", at line: ").append(oce.getBegin().get().line)
                                        .append(". Instance of ").append(cjClassName)
                                        .append(" is created and used directly.  ");
                            }
                        }
                    });
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }

    }

    // Class Member Variable Usage Variable (CMAUA)
    public String checkCMAUA(String ciFilePath, String cjFilePath) {
        /*
        An instance of class Cj, cj, is a member variable of class Ci, which is then used in Ci's code.
        public class MyCi {
            private MyCj myCj;

            public void someMethod() {
                if (myCj != null) {
                    System.out.println("myCj is not null");
                }
            }

            public void anotherMethod() {
                if (myCj != null) {
                    myCj.method1();
                }
            }

            public void thirdMethod() {
                if (myCj != null) {
                    int value = myCj.memberVariable;
                }
            }

            public void fourthMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    System.out.println("myCjParam is not null");
                }
            }
        }
        public class MyCj {
            public void method1() {
                // Do something...
            }

            public int memberVariable = 0;
        }
         */
        JavaParser javaParser = new JavaParser();
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cjd -> !cjd.isInterface());
            String cjClassName = cjClassOpt.get().getNameAsString();
            if (!cjClassOpt.isPresent()) return "";


            Optional<ClassOrInterfaceDeclaration> ciClassOpt = ciCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cid -> !cid.isInterface());
            String ciClassName = ciClassOpt.get().getNameAsString();
            if (!ciClassOpt.isPresent()) return "";

            ClassOrInterfaceDeclaration ciClass = ciClassOpt.get();
            Map<String, FieldDeclaration> cjFields = new HashMap<>();

            ciClass.getFields().forEach(field -> {
                field.getVariables().forEach(variable -> {
                    if (variable.getType().toString().equals(cjClassName)) {
                        cjFields.put(variable.getName().asString(), field);
                    }
                });
            });

            // Finding direct use of Cj member variables in Ci classes
            ciClass.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    // Find direct use of Cj member variables (not by calling member methods or accessing member variables)
                    md.findAll(NameExpr.class).forEach(nameExpr -> {
                        String name = nameExpr.getName().getId();
                        if (cjFields.containsKey(name)) {
                            // Make sure this is not a member method call or member variable access
                            Node parentNode = nameExpr.getParentNode().orElse(null);
                            if (!(parentNode instanceof MethodCallExpr || parentNode instanceof FieldAccessExpr)) {
                                couplingInfo.append("Coupling found in method ").append(md.getName())
                                        .append(", at line: ").append(nameExpr.getBegin().get().line)
                                        .append(". Instance of ").append(cjClassName)
                                        .append(" member variable ").append(name)
                                        .append(" is used directly.  ");
                            }
                        }
                    });
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }

    }

    // Function Parameter Usage Variable (FPUA)
    public String checkFPUA(String ciFilePath, String cjFilePath) {
        /*
        public class MyCi {

            public void someMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    System.out.println("myCjParam is not null");
                }
            }

            public void anotherMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    myCjParam.method1();
                }
            }

            public void thirdMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    int value = myCjParam.memberVariable;
                }
            }
        }
        public class MyCj {
            public void method1() {
                // Do something...
            }

            public int memberVariable = 0;
        }
         */
        JavaParser javaParser = new JavaParser();
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cjd -> !cjd.isInterface());
            String cjClassName = cjClassOpt.get().getNameAsString();
            if (!cjClassOpt.isPresent()) return "";

            Optional<ClassOrInterfaceDeclaration> ciClassOpt = ciCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cid -> !cid.isInterface());
            String ciClassName = ciClassOpt.get().getNameAsString();
            if (!ciClassOpt.isPresent()) return "";

            ClassOrInterfaceDeclaration ciClass = ciClassOpt.get();

            // Look for methods of class Ci that take parameters of type Cj and check for direct use of cj itself within the method body
            ciClass.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    // Collects the names of the method parameters of type Cj
                    Map<String, Parameter> cjParams = new HashMap<>();
                    md.getParameters().forEach(param -> {
                        if (param.getType().toString().equals(cjClassName)) {
                            cjParams.put(param.getName().asString(), param);
                        }
                    });

                    if (!cjParams.isEmpty()) {
                        md.findAll(NameExpr.class).forEach(nameExpr -> {
                            String paramName = nameExpr.getName().getId();
                            if (cjParams.containsKey(paramName)) {
                                Node parentNode = nameExpr.getParentNode().orElse(null);
                                // 确保这不是一个成员方法调用或成员变量访问
                                if (!(parentNode instanceof MethodCallExpr || parentNode instanceof FieldAccessExpr)) {
                                    couplingInfo.append("Coupling found in method ").append(md.getName())
                                            .append(", at line: ").append(nameExpr.getBegin().get().line)
                                            .append(". Instance of ").append(cjClassName)
                                            .append(" parameter ").append(paramName)
                                            .append(" is used directly.  ");
                                }
                            }
                        });
                    }
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }
    }

    // Static Variable Invoking (SAI)
    public String checkStaticVariableInvoking(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            String classCjName = cjFilePath.substring(cjFilePath.lastIndexOf("/") + 1, cjFilePath.lastIndexOf("."));

            // Get all static field declarations in Cj
            Set<String> staticVariables = cj.findAll(FieldDeclaration.class)
                    .stream()
                    .filter(field -> field.getModifiers().contains(Modifier.staticModifier()))
                    .flatMap(field -> field.getVariables().stream())
                    .map(variable -> classCjName + "." + variable.getNameAsString())
                    .collect(Collectors.toSet());

            // Find all method declarations in Ci and check if they internally reference static variables in Cj
            ci.findAll(MethodDeclaration.class).forEach(method -> {
                method.findAll(FieldAccessExpr.class).forEach(fieldAccess -> {
                    if (fieldAccess.getScope() instanceof NameExpr &&
                            ((NameExpr) fieldAccess.getScope()).getNameAsString().equals(classCjName) &&
                            staticVariables.contains(fieldAccess.toString())) {
                        result.append("Static Variable Invoking found: ").append(method.getName())
                                .append(" invokes static variable ").append(fieldAccess.getNameAsString()).append(",  ");
                    }
                });
            });

            return result.length() > 0 ? result.toString() : "";
        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Method Member Variable Invoking (MMAIA)
    public String checkMMAIA(String ciFilePath, String cjFilePath) {
        /*
        A method of class Ci defines an instance cj of Cj, and then the code uses the instance cj of Cj to call other members of Cj.
        public class Cj {
            public int field1;
            public String field2;

            public void doSomething() {
                // Do something...
            }
        }
        public class Ci {
            public void someMethod() {
                Cj cj = new Cj();
                System.out.println(cj.field1);
                System.out.println(cj.field2);
            }

            public void anotherMethod() {
                Cj cj = new Cj();
                cj.doSomething();
            }

            public void thirdMethod() {
                Cj cj = new Cj();
                System.out.println("Just creating an instance of Cj but not using its fields.");
            }
        }
         */
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findAll(ClassOrInterfaceDeclaration.class).stream()
                    .filter(cjd -> !cjd.isInterface())
                    .findFirst();
            if (!cjClassOpt.isPresent()) return "";
            String cjClassName = cjClassOpt.get().getNameAsString();

            ciCU.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    Map<String, ObjectCreationExpr> createdInstances = new HashMap<>();
                    md.accept(new VoidVisitorAdapter<Void>() {
                        @Override
                        public void visit(ObjectCreationExpr oce, Void arg) {
                            super.visit(oce, arg);
                            if (oce.getType().toString().equals(cjClassName)) {
                                // 查找赋值语句，获取变量名
                                if (oce.getParentNode().isPresent() && oce.getParentNode().get() instanceof VariableDeclarator) {
                                    VariableDeclarator vd = (VariableDeclarator) oce.getParentNode().get();
                                    createdInstances.put(vd.getName().asString(), oce);
                                }
                            }
                        }
                    }, null);

                    md.findAll(FieldAccessExpr.class).forEach(fieldAccess -> {
                        if (fieldAccess.getScope() != null) {
                            if (fieldAccess.getScope() instanceof NameExpr) {
                                NameExpr scopeName = (NameExpr) fieldAccess.getScope();
                                if (createdInstances.containsKey(scopeName.getName().asString())) {
                                    couplingInfo.append("Coupling found in method ").append(md.getName())
                                            .append(", at line: ").append(fieldAccess.getBegin().get().line)
                                            .append(". Instance of ").append(cjClassName)
                                            .append(" is used to access member variable.  ");
                                }
                            }
                        }
                    });
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }
    }

    // Class Member Variable Invoking Variable (CMAIA)
    public String checkCMAIA(String ciFilePath, String cjFilePath) {
        /*
        An instance of class Cj, cj, is a member variable of class Ci, and then Ci's code uses the member variable cj to call a member variable of class Cj.
        public class MyCj {
            public int memberVariable = 0;
        }
        public class MyCi {
            private MyCj myCj;

            public void someMethod() {
                if (myCj != null) {
                    int value = myCj.memberVariable;
                }
            }

            public void anotherMethod() {
                if (myCj != null) {
                    System.out.println("myCj is not null");
                }
            }

            public void thirdMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    int value = myCjParam.memberVariable;
                }
            }
        }
         */
        JavaParser javaParser = new JavaParser();
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cjd -> !cjd.isInterface());
            String cjClassName = cjClassOpt.get().getNameAsString();
            if (!cjClassOpt.isPresent()) {
                String s = cjClassName + "file does not contain a valid class.";
                return "";
            }

            Optional<ClassOrInterfaceDeclaration> ciClassOpt = ciCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cid -> !cid.isInterface());
            String ciClassName = ciClassOpt.get().getNameAsString();
            if (!ciClassOpt.isPresent()) return "";

            ClassOrInterfaceDeclaration ciClass = ciClassOpt.get();
            Map<String, FieldDeclaration> cjFields = new HashMap<>();

            ciClass.getFields().forEach(field -> {
                field.getVariables().forEach(variable -> {
                    if (variable.getType().toString().equals(cjClassName)) {
                        cjFields.put(variable.getName().asString(), field);
                    }
                });
            });

            ciClass.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    md.findAll(FieldAccessExpr.class).forEach(fieldAccess -> {
                        Expression scope = fieldAccess.getScope();
                        if (scope instanceof NameExpr && cjFields.containsKey(((NameExpr) scope).getName().getId())) {
                            String accessedFieldName = fieldAccess.getName().asString();
                            String memberVariableName = ((NameExpr) scope).getName().getId();
                            if (!accessedFieldName.equals(memberVariableName)) {
                                couplingInfo.append("Coupling found in method ").append(md.getName())
                                        .append(", at line: ").append(fieldAccess.getBegin().get().line)
                                        .append(". Instance of ").append(cjClassName)
                                        .append(" member variable ").append(memberVariableName)
                                        .append(" is used to access "+ cjClassName + "'s member variable ")
                                        .append(accessedFieldName).append(".  ");
                            }
                        }
                    });
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }
    }

    // Function Parameter Invoking Variable (FPIA)
    public String checkFPIA(String ciFilePath, String cjFilePath) {
        /*
        An instance of class Cj, cj, is a function parameter for a method of class Ci, and then cj is used in Ci's code to call a member variable of Cj.
        public class MyCi {

            public void someMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    int value = myCjParam.memberVariable;
                }
            }

            public void anotherMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    System.out.println("myCjParam is not null");
                }
            }

            public void thirdMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    myCjParam.method1();
                }
            }
        }
        public class MyCj {
            public void method1() {
                // Do something...
            }

            public int memberVariable = 0;
        }
         */
        JavaParser javaParser = new JavaParser();
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cjd -> !cjd.isInterface());
            String cjClassName = cjClassOpt.get().getNameAsString();
            if (!cjClassOpt.isPresent()) return "";

            Optional<ClassOrInterfaceDeclaration> ciClassOpt = ciCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cid -> !cid.isInterface());
            String ciClassName = ciClassOpt.get().getNameAsString();
            if (!ciClassOpt.isPresent()) return "";

            ClassOrInterfaceDeclaration ciClass = ciClassOpt.get();

            ciClass.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    Map<String, Parameter> cjParams = new HashMap<>();
                    md.getParameters().forEach(param -> {
                        if (param.getType().toString().equals(cjClassName)) {
                            cjParams.put(param.getName().asString(), param);
                        }
                    });

                    if (!cjParams.isEmpty()) {
                        md.findAll(FieldAccessExpr.class).forEach(fieldAccess -> {
                            Expression scope = fieldAccess.getScope();
                            if (scope instanceof NameExpr && cjParams.containsKey(((NameExpr) scope).getName().getId())) {
                                String paramName = ((NameExpr) scope).getName().getId();
                                String accessedFieldName = fieldAccess.getName().asString();
                                if (!accessedFieldName.equals(paramName)) {
                                    couplingInfo.append("Coupling found in method ").append(md.getName())
                                            .append(", at line: ").append(fieldAccess.getBegin().get().line)
                                            .append(". Instance of ").append(cjClassName)
                                            .append(" parameter ").append(paramName)
                                            .append(" is used to access " + cjClassName + "'s member variable ")
                                            .append(accessedFieldName).append(".  ");
                                }
                            }
                        });
                    }
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }
    }

    // Static Method Invoking (SMI)
    public String checkStaticMethodInvoking(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();
            CompilationUnit cj = cjParseResult.getResult().get();

            String classCjName = cjFilePath.substring(cjFilePath.lastIndexOf("/") + 1, cjFilePath.lastIndexOf("."));

            Set<String> staticMethods = cj.findAll(MethodDeclaration.class)
                    .stream()
                    .filter(method -> method.getModifiers().contains(Modifier.staticModifier()))
                    .map(MethodDeclaration::getNameAsString)
                    .collect(Collectors.toSet());

            ci.findAll(MethodCallExpr.class).forEach(methodCall -> {
                if (methodCall.getScope().isPresent() && methodCall.getScope().get() instanceof NameExpr) {
                    NameExpr scopeName = (NameExpr) methodCall.getScope().get();
                    String className = scopeName.getNameAsString();

                    if (classCjName.equals(className) && staticMethods.contains(methodCall.getNameAsString())) {
                        result.append("Static Method Invoking found: ").append(methodCall.toString()).append(",  ");
                    }
                }
            });

            return result.length() > 0 ? result.toString() : "";
        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Construction Method Invoking (CMI)
    public String checkConstructionMethodInvoking(String ciFilePath, String cjFilePath) throws IOException {
        StringBuilder result = new StringBuilder();
        ParserConfiguration parserConfiguration = new ParserConfiguration();
        JavaParser javaParser = new JavaParser(parserConfiguration);

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ci = ciParseResult.getResult().get();

            String classCjName = cjFilePath.substring(cjFilePath.lastIndexOf("/") + 1, cjFilePath.lastIndexOf("."));

            ci.findAll(ObjectCreationExpr.class).forEach(objectCreation -> {
                if (classCjName.equals(objectCreation.getType().toString())) {
                    result.append("Construction Method Invoking found: ").append(objectCreation.toString()).append(",  ");
                }
            });

            return result.length() > 0 ? result.toString() : "";
        } catch (FileNotFoundException e) {
            return "";
        } catch (ParseProblemException e) {
            return "";
        }
    }

    // Function Parameter Invoking Method (FPIM)
    public String checkFPIM(String ciFilePath, String cjFilePath) {
        /*
        An instance of class Cj, cj, is a function parameter for a method of class Ci, and then cj is used in Ci's code to call a member method of Cj.
        class Ci {
            void method(Cj cj) {
                int k = cj.getk();
            }
        }
         */
        JavaParser javaParser = new JavaParser();
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cjd -> !cjd.isInterface());
            String cjClassName = cjClassOpt.get().getNameAsString();
            if (!cjClassOpt.isPresent()) return "";


            Optional<ClassOrInterfaceDeclaration> ciClassOpt = ciCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cid -> !cid.isInterface());
            String ciClassName = ciClassOpt.get().getNameAsString();
            if (!ciClassOpt.isPresent()) return "";

            ClassOrInterfaceDeclaration ciClass = ciClassOpt.get();

            ciClass.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    Map<String, Parameter> cjParams = new HashMap<>();
                    md.getParameters().forEach(param -> {
                        if (param.getType().toString().equals(cjClassName)) {
                            cjParams.put(param.getName().asString(), param);
                        }
                    });

                    if (!cjParams.isEmpty()) {
                        md.findAll(MethodCallExpr.class).forEach(methodCall -> {
                            Expression scope = methodCall.getScope().orElse(null);
                            if (scope instanceof NameExpr && cjParams.containsKey(((NameExpr) scope).getName().getId())) {
                                String paramName = ((NameExpr) scope).getName().getId();
                                String calledMethodName = methodCall.getName().asString();
                                couplingInfo.append("Coupling found in method ").append(md.getName())
                                        .append(", at line: ").append(methodCall.getBegin().get().line)
                                        .append(". Instance of ").append(cjClassName)
                                        .append(" parameter ").append(paramName)
                                        .append(" is used to call" + cjClassName + "'s method ")
                                        .append(calledMethodName).append(".  ");
                            }
                        });
                    }
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }
    }

    // Method Member Variable Invoking Method (MMAIM)
    public String checkMMAIM(String ciFilePath, String cjFilePath) {
        /*
        A method of class Ci defines an instance cj of Cj, which is then used in the code to call a member method of Cj.
        public class Cj {
            public void method1() {
                // Do something...
            }

            public void method2() {
                // Do something else...
            }
        }
        public class Ci {
            public void someMethod() {
                Cj cj = new Cj();
                cj.method1();
            }

            public void anotherMethod() {
                Cj cj = new Cj();
                cj.method2();
            }

            public void thirdMethod() {
                Cj cj = new Cj();
                System.out.println("Just creating an instance of Cj but not calling its methods.");
            }

            public void fourthMethod(Cj cj) {
                cj.method1();
            }
        }
         */
        JavaParser javaParser = new JavaParser();
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cjd -> !cjd.isInterface());
            if (!cjClassOpt.isPresent()) return "";
            String cjClassName = cjClassOpt.get().getNameAsString();

            ciCU.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    Map<String, ObjectCreationExpr> createdInstances = new HashMap<>();
                    md.findAll(ObjectCreationExpr.class).forEach(oce -> {
                        if (oce.getType().toString().equals(cjClassName)) {
                            oce.getParentNode().ifPresent(parent -> {
                                if (parent instanceof VariableDeclarator) {
                                    VariableDeclarator vd = (VariableDeclarator) parent;
                                    createdInstances.put(vd.getName().asString(), oce);
                                }
                            });
                        }
                    });

                    md.findAll(MethodCallExpr.class).forEach(methodCall -> {
                        methodCall.getScope().ifPresent(scope -> {
                            if (scope instanceof NameExpr) {
                                NameExpr scopeName = (NameExpr) scope;
                                if (createdInstances.containsKey(scopeName.getName().asString())) {
                                    couplingInfo.append("Coupling found in method ").append(md.getName())
                                            .append(", at line: ").append(methodCall.getBegin().get().line)
                                            .append(". Instance of ").append(cjClassName)
                                            .append(" is used to call member method.  ");
                                }
                            }
                        });
                    });
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }
    }

    // Class Member Variable Invoking Method (CMAIM)
    public String checkCMAIM(String ciFilePath, String cjFilePath) {
        /*
        An instance of class Cj, cj, is a member variable of class Ci, which is then used in Ci's code to call a member method of class Cj.
        public class MyCi {
            private MyCj myCj;

            public void someMethod() {
                if (myCj != null) {
                    myCj.method1();
                }
            }

            public void anotherMethod() {
                if (myCj != null) {
                    System.out.println("myCj is not null");
                }
            }

            public void thirdMethod(MyCj myCjParam) {
                if (myCjParam != null) {
                    myCjParam.method1();
                }
            }
        }
        public class MyCj {
            public void method1() {
                // Do something...
            }
        }
         */
        JavaParser javaParser = new JavaParser();
        StringBuilder couplingInfo = new StringBuilder();

        try (FileInputStream ciStream = new FileInputStream(ciFilePath);
             FileInputStream cjStream = new FileInputStream(cjFilePath)) {

            ParseResult<CompilationUnit> ciParseResult = javaParser.parse(ciStream);
            ParseResult<CompilationUnit> cjParseResult = javaParser.parse(cjStream);

            if (!ciParseResult.isSuccessful() || !cjParseResult.isSuccessful()) {
                return "";
            }

            CompilationUnit ciCU = ciParseResult.getResult().get();
            CompilationUnit cjCU = cjParseResult.getResult().get();

            Optional<ClassOrInterfaceDeclaration> cjClassOpt = cjCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cjd -> !cjd.isInterface());
            String cjClassName = cjClassOpt.get().getNameAsString();
            if (!cjClassOpt.isPresent()) return "";

            Optional<ClassOrInterfaceDeclaration> ciClassOpt = ciCU.findFirst(ClassOrInterfaceDeclaration.class)
                    .filter(cid -> !cid.isInterface());
            String ciClassName = ciClassOpt.get().getNameAsString();
            if (!ciClassOpt.isPresent()) return "";

            ClassOrInterfaceDeclaration ciClass = ciClassOpt.get();
            Map<String, FieldDeclaration> cjFields = new HashMap<>();

            ciClass.getFields().forEach(field -> {
                field.getVariables().forEach(variable -> {
                    if (variable.getType().toString().equals(cjClassName)) {
                        cjFields.put(variable.getName().asString(), field);
                    }
                });
            });

            ciClass.accept(new VoidVisitorAdapter<Void>() {
                @Override
                public void visit(MethodDeclaration md, Void arg) {
                    super.visit(md, arg);

                    md.findAll(MethodCallExpr.class).forEach(methodCall -> {
                        Expression scope = methodCall.getScope().orElse(null);
                        if (scope instanceof NameExpr && cjFields.containsKey(((NameExpr) scope).getName().getId())) {
                            String memberVariableName = ((NameExpr) scope).getName().getId();
                            couplingInfo.append("Coupling found in method ").append(md.getName())
                                    .append(", at line: ").append(methodCall.getBegin().get().line)
                                    .append(". Instance of ").append(cjClassName)
                                    .append(" member variable ").append(memberVariableName)
                                    .append(" is used to call " + cjClassName + "'s method ")
                                    .append(methodCall.getName()).append(".  ");
                        }
                    });
                }
            }, null);

            return couplingInfo.toString().isEmpty() ? "" : couplingInfo.toString();
        } catch (Exception e) {
            return "";
        }
    }

    public static void main( String[] args ) throws IOException {
        if (args.length != 2) {
            System.err.println("Usage: java coupling_dependency <ci> <cj>");
            return;
        }

        String ci = args[0];
        String cj = args[1];

        App cd = new App();

        List<String> arr = new ArrayList<>();
        String IH = cd.checkInheritance(ci, cj);
        if (!IH.equals("")) {
            IH = "Inheritance(IH): " + IH;
            arr.add(IH);
        }

        String II = cd.checkInterfaceImplementation(ci, cj);
        if (!II.equals("")) {
            II = "InterfaceImplementation(II): " + II;
            arr.add(II);
        }

        String TC = cd.checkTypeCasting(ci, cj);
        if (!TC.equals("")) {
            TC = "TypeCasting(TC): " + TC;
            arr.add(TC);
        }

        String IO = cd.checkInstanceof(ci, cj);
        if (!IO.equals("")) {
            IO = "Instanceof(IO): " + IO;
            arr.add(IO);
        }

        String RT = cd.checkReturnType(ci, cj);
        if (!RT.equals("")) {
            RT = "ReturnType(RT): " + RT;
            arr.add(RT);
        }

        String ET = cd.checkExceptionThrows(ci, cj);
        if (!ET.equals("")) {
            ET = "ExceptionThrows(ET): " + ET;
            arr.add(ET);
        }

        String MMAUA = cd.checkMMAUA(ci, cj);
        if (!MMAUA.equals("")) {
            MMAUA = "Method Member Variable Usage Variable (MMAUA): " + MMAUA;
            arr.add(MMAUA);
        }

        String CMAUA = cd.checkCMAUA(ci, cj);
        if (!CMAUA.equals("")) {
            CMAUA = "Class Member Variable Usage Variable (CMAUA): " + CMAUA;
            arr.add(CMAUA);
        }

        String FPUA = cd.checkFPUA(ci, cj);
        if (!FPUA.equals("")) {
            FPUA = "Function Parameter Usage Variable (FPUA): " + FPUA;
            arr.add(FPUA);
        }

        String SAI = cd.checkStaticVariableInvoking(ci, cj);
        if (!SAI.equals("")) {
            SAI = "StaticVariableInvoking(SAI): " + SAI;
            arr.add(SAI);
        }

        String MMAIA = cd.checkMMAIA(ci, cj);
        if (!MMAIA.equals("")) {
            MMAIA = "Method Member Variable Invoking (MMAIA): " + MMAIA;
            arr.add(MMAIA);
        }

        String CMAIA = cd.checkCMAIA(ci, cj);
        if (!CMAIA.equals("")) {
            CMAIA = "Class Member Variable Invoking Variable (CMAIA): " + CMAIA;
            arr.add(CMAIA);
        }

        String FPIA = cd.checkFPIA(ci, cj);
        if (!FPIA.equals("")) {
            FPIA = "Function Parameter Invoking Variable (FPIA): " + FPIA;
            arr.add(FPIA);
        }

        String SMI = cd.checkStaticMethodInvoking(ci, cj);
        if (!SMI.equals("")) {
            SMI = "StaticMethodInvoking(SMI): " + SMI;
            arr.add(SMI);
        }

        String CMI = cd.checkConstructionMethodInvoking(ci, cj);
        if (!CMI.equals("")) {
            CMI = "ConstructorInvoking(CMI): " + CMI;
            arr.add(CMI);
        }

        String FPIM = cd.checkFPIM(ci, cj);
        if (!FPIM.equals("")) {
            FPIM = "Function Parameter Invoking Method (FPIM): " + FPIM;
            arr.add(FPIM);
        }

        String MMAIM = cd.checkMMAIM(ci, cj);
        if (!MMAIM.equals("")) {
            MMAIM = "Method Member Variable Invoking Method (MMAIM): " + MMAIM;
            arr.add(MMAIM);
        }

        String CMAIM = cd.checkCMAIM(ci, cj);
        if (!CMAIM.equals("")) {
            CMAIM = "ConstructorInvoking(CMAIM): " + CMAIM;
            arr.add(CMAIM);
        }

        if (arr.isEmpty()) {
            System.out.println("There are no coupling dependencies between these two entities");
        }

        for (String s : arr) {
            System.out.println(s);
        }
    }
}

