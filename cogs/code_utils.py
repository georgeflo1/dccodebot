import discord
from discord.ext import commands

SNIPPETS = {
    "python": {
        "for": "for i in range(n):\n    pass",
        "while": "while condition:\n    pass",
        "if": "if condition:\n    pass\nelse:\n    pass",
        "function": "def my_function(param):\n    return param",
        "class": "class MyClass:\n    def __init__(self):\n        pass",
        "try": "try:\n    pass\nexcept Exception as e:\n    print(e)",
        "list_comp": "[x for x in range(n)]",
        "dict": 'my_dict = {"key": "value"}',
        "open_file": 'with open("file.txt", "r") as f:\n    content = f.read()',
        "import": "import os\nimport sys",
        "async": "async def my_async_func():\n    await some_coroutine()",
        "lambda": "my_func = lambda x: x * 2",
    },
    "javascript": {
        "for": "for (let i = 0; i < n; i++) {\n    // ...\n}",
        "while": "while (condition) {\n    // ...\n}",
        "if": "if (condition) {\n    // ...\n} else {\n    // ...\n}",
        "function": "function myFunction(param) {\n    return param;\n}",
        "arrow": "const myFunc = (param) => param;",
        "class": "class MyClass {\n    constructor() {\n        // ...\n    }\n}",
        "try": "try {\n    // ...\n} catch (error) {\n    console.error(error);\n}",
        "dom": 'document.getElementById("myId").addEventListener("click", (e) => {});',
        "import": 'import { something } from "module";',
        "export": "export default function myFunc() {}",
        "array_map": "const mapped = arr.map(item => item * 2);",
        "array_filter": "const filtered = arr.filter(item => item > 0);",
    },
    "java": {
        "for": "for (int i = 0; i < n; i++) {\n    // ...\n}",
        "while": "while (condition) {\n    // ...\n}",
        "if": "if (condition) {\n    // ...\n} else {\n    // ...\n}",
        "method": "public void myMethod(String param) {\n    // ...\n}",
        "class": "public class MyClass {\n    public MyClass() {\n        // ...\n    }\n}",
        "try": "try {\n    // ...\n} catch (Exception e) {\n    e.printStackTrace();\n}",
        "main": "public static void main(String[] args) {\n    // ...\n}",
        "interface": "public interface MyInterface {\n    void myMethod();\n}",
        "list": "List<String> list = new ArrayList<>();",
        "map": "Map<String, Integer> map = new HashMap<>();",
    },
    "csharp": {
        "for": "for (int i = 0; i < n; i++)\n{\n    // ...\n}",
        "while": "while (condition)\n{\n    // ...\n}",
        "if": "if (condition)\n{\n    // ...\n}\nelse\n{\n    // ...\n}",
        "method": "public void MyMethod(string param)\n{\n    // ...\n}",
        "class": "public class MyClass\n{\n    public MyClass()\n    {\n        // ...\n    }\n}",
        "async": "public async Task<string> MyAsyncMethod()\n{\n    await Task.Delay(1000);\n    return \"done\";\n}",
        "linq": "var result = list.Where(x => x > 0).Select(x => x * 2);",
    },
    "c": {
        "for": "for (int i = 0; i < n; i++) {\n    // ...\n}",
        "while": "while (condition) {\n    // ...\n}",
        "if": "if (condition) {\n    // ...\n} else {\n    // ...\n}",
        "main": "int main() {\n    return 0;\n}",
        "function": "void my_function(int param) {\n    // ...\n}",
        "struct": "struct MyStruct {\n    int x;\n    int y;\n};",
        "malloc": "int *ptr = (int *)malloc(n * sizeof(int));",
        "printf": 'printf("Value: %d\\n", value);',
    },
    "cpp": {
        "for": "for (int i = 0; i < n; i++) {\n    // ...\n}",
        "while": "while (condition) {\n    // ...\n}",
        "if": "if (condition) {\n    // ...\n} else {\n    // ...\n}",
        "main": "int main() {\n    return 0;\n}",
        "function": "void myFunction(int param) {\n    // ...\n}",
        "class": "class MyClass {\npublic:\n    MyClass() {}\n};",
        "vector": "std::vector<int> vec;",
        "cout": 'std::cout << "Hello" << std::endl;',
        "string": 'std::string str = "hello";',
    },
    "php": {
        "for": "for ($i = 0; $i < $n; $i++) {\n    // ...\n}",
        "while": "while ($condition) {\n    // ...\n}",
        "if": "if ($condition) {\n    // ...\n} else {\n    // ...\n}",
        "function": "function myFunction($param) {\n    return $param;\n}",
        "class": "class MyClass {\n    public function __construct() {\n        // ...\n    }\n}",
        "array": "$arr = [1, 2, 3];",
        "foreach": "foreach ($arr as $item) {\n    // ...\n}",
    },
    "sql": {
        "select": "SELECT column1, column2\nFROM table_name\nWHERE condition;",
        "insert": "INSERT INTO table_name (col1, col2)\nVALUES ('val1', 'val2');",
        "update": "UPDATE table_name\nSET column1 = 'value'\nWHERE condition;",
        "delete": "DELETE FROM table_name\nWHERE condition;",
        "join": "SELECT * FROM table1\nINNER JOIN table2 ON table1.id = table2.id;",
        "create": "CREATE TABLE table_name (\n    id INT PRIMARY KEY,\n    name VARCHAR(255)\n);",
    },
    "html": {
        "basic": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Title</title>\n</head>\n<body>\n    <h1>Hello</h1>\n</body>\n</html>",
        "form": '<form action="/submit" method="POST">\n    <input type="text" name="name">\n    <button type="submit">Submit</button>\n</form>',
        "div": '<div class="container">\n    <p>Content</p>\n</div>',
    },
    "css": {
        "basic": ".class {\n    property: value;\n}",
        "flexbox": ".container {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n}",
        "grid": ".grid {\n    display: grid;\n    grid-template-columns: 1fr 1fr;\n    gap: 10px;\n}",
        "responsive": "@media (max-width: 768px) {\n    .class {\n        property: value;\n    }\n}",
    },
    "rust": {
        "fn": "fn my_function(param: i32) -> i32 {\n    param\n}",
        "struct": "struct MyStruct {\n    field: i32,\n}",
        "impl": "impl MyStruct {\n    fn new() -> Self {\n        MyStruct { field: 0 }\n    }\n}",
        "match": "match value {\n    1 => \"one\",\n    2 => \"two\",\n    _ => \"other\",\n};",
        "vector": "let vec: Vec<i32> = Vec::new();",
    },
    "go": {
        "func": "func myFunction(param int) int {\n    return param\n}",
        "struct": "type MyStruct struct {\n    Field int\n}",
        "interface": "type MyInterface interface {\n    MyMethod()\n}",
        "goroutine": "go func() {\n    // ...\n}()",
        "slice": "slice := []int{1, 2, 3}",
    },
}

LANGUAGES = {
    "python": ("Python", "py"),
    "javascript": ("JavaScript", "js"),
    "java": ("Java", "java"),
    "csharp": ("C#", "cs"),
    "c": ("C", "c"),
    "cpp": ("C++", "cpp"),
    "php": ("PHP", "php"),
    "sql": ("SQL", "sql"),
    "html": ("HTML", "html"),
    "css": ("CSS", "css"),
    "rust": ("Rust", "rs"),
    "go": ("Go", "go"),
}


class CodeUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="snippet", aliases=["ornek", "kodornegi", "template"])
    async def snippet(self, ctx, dil: str, *, arama: str = None):
        dil = dil.lower()
        if dil not in SNIPPETS:
            await ctx.send(f"Desteklenmeyen dil: `{dil}`. `{self.bot.command_prefix}diller` ile bakabilirsin.")
            return

        if arama:
            arama = arama.lower().replace(" ", "_")
            if arama in SNIPPETS[dil]:
                lang_name, ext = LANGUAGES.get(dil, (dil, dil))
                code = SNIPPETS[dil][arama]
                embed = discord.Embed(
                    title=f"{lang_name} - {arama}",
                    color=discord.Color.green(),
                )
                embed.add_field(name="Kod", value=f"```{ext}\n{code}\n```", inline=False)
                await ctx.send(embed=embed)
            else:
                available = ", ".join(SNIPPETS[dil].keys())
                await ctx.send(f"`{arama}` bulunamadi. Mevcut snippetler: `{available}`")
        else:
            available = ", ".join(SNIPPETS[dil].keys())
            lang_name = LANGUAGES.get(dil, (dil, dil))[0]
            embed = discord.Embed(
                title=f"{lang_name} Snippetleri",
                description=f"Kullanim: `{self.bot.command_prefix}snippet {dil} <isim>`\n\nMevcut: `{available}`",
                color=discord.Color.blue(),
            )
            await ctx.send(embed=embed)

    @commands.command(name="diller", aliases=["languages", "lang"])
    async def diller(self, ctx):
        embed = discord.Embed(
            title="Desteklenen Diller",
            description="Kod snippetleri icin desteklenen diller:",
            color=discord.Color.gold(),
        )

        for dil_key, (lang_name, ext) in LANGUAGES.items():
            snippet_count = len(SNIPPETS.get(dil_key, {}))
            embed.add_field(
                name=f"{lang_name} (`.{ext}`)",
                value=f"{snippet_count} snippet mevcut",
                inline=True,
            )

        embed.set_footer(text=f"Kullanim: {self.bot.command_prefix}snippet <dil> | {self.bot.command_prefix}snippet <dil> <isim>")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CodeUtils(bot))
