#pragma checksum "F:\DeIdWeb\數位部\資安院\deidweb_v2_k\DeIdWeb_V2_K\Views\Dept\DeptList.cshtml" "{ff1816ec-aa5e-4d10-87f7-6f4963833460}" "a521ff081e75de8d7c53c73385bc83b44fa244e6"
// <auto-generated/>
#pragma warning disable 1591
[assembly: global::Microsoft.AspNetCore.Razor.Hosting.RazorCompiledItemAttribute(typeof(AspNetCore.Views_Dept_DeptList), @"mvc.1.0.view", @"/Views/Dept/DeptList.cshtml")]
namespace AspNetCore
{
    #line hidden
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Threading.Tasks;
    using Microsoft.AspNetCore.Mvc;
    using Microsoft.AspNetCore.Mvc.Rendering;
    using Microsoft.AspNetCore.Mvc.ViewFeatures;
#nullable restore
#line 1 "F:\DeIdWeb\數位部\資安院\deidweb_v2_k\DeIdWeb_V2_K\Views\_ViewImports.cshtml"
using DeIdWeb_V2_K;

#line default
#line hidden
#nullable disable
#nullable restore
#line 2 "F:\DeIdWeb\數位部\資安院\deidweb_v2_k\DeIdWeb_V2_K\Views\_ViewImports.cshtml"
using DeIdWeb_V2_K.Models;

#line default
#line hidden
#nullable disable
#nullable restore
#line 1 "F:\DeIdWeb\數位部\資安院\deidweb_v2_k\DeIdWeb_V2_K\Views\Dept\DeptList.cshtml"
using System.Globalization;

#line default
#line hidden
#nullable disable
#nullable restore
#line 2 "F:\DeIdWeb\數位部\資安院\deidweb_v2_k\DeIdWeb_V2_K\Views\Dept\DeptList.cshtml"
using Resources;

#line default
#line hidden
#nullable disable
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"a521ff081e75de8d7c53c73385bc83b44fa244e6", @"/Views/Dept/DeptList.cshtml")]
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"f7e853e99b4cd50ed2f7f7df1acd9abe40c6c468", @"/Views/_ViewImports.cshtml")]
    public class Views_Dept_DeptList : global::Microsoft.AspNetCore.Mvc.Razor.RazorPage<dynamic>
    {
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_0 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("class", new global::Microsoft.AspNetCore.Html.HtmlString("search_form"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_1 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("class", new global::Microsoft.AspNetCore.Html.HtmlString("form"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_2 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("action", new global::Microsoft.AspNetCore.Html.HtmlString(""), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_3 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("method", "post", global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_4 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("role", new global::Microsoft.AspNetCore.Html.HtmlString("form"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        #line hidden
        #pragma warning disable 0649
        private global::Microsoft.AspNetCore.Razor.Runtime.TagHelpers.TagHelperExecutionContext __tagHelperExecutionContext;
        #pragma warning restore 0649
        private global::Microsoft.AspNetCore.Razor.Runtime.TagHelpers.TagHelperRunner __tagHelperRunner = new global::Microsoft.AspNetCore.Razor.Runtime.TagHelpers.TagHelperRunner();
        #pragma warning disable 0169
        private string __tagHelperStringValueBuffer;
        #pragma warning restore 0169
        private global::Microsoft.AspNetCore.Razor.Runtime.TagHelpers.TagHelperScopeManager __backed__tagHelperScopeManager = null;
        private global::Microsoft.AspNetCore.Razor.Runtime.TagHelpers.TagHelperScopeManager __tagHelperScopeManager
        {
            get
            {
                if (__backed__tagHelperScopeManager == null)
                {
                    __backed__tagHelperScopeManager = new global::Microsoft.AspNetCore.Razor.Runtime.TagHelpers.TagHelperScopeManager(StartTagHelperWritingScope, EndTagHelperWritingScope);
                }
                return __backed__tagHelperScopeManager;
            }
        }
        private global::Microsoft.AspNetCore.Mvc.TagHelpers.FormTagHelper __Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper;
        private global::Microsoft.AspNetCore.Mvc.TagHelpers.RenderAtEndOfFormTagHelper __Microsoft_AspNetCore_Mvc_TagHelpers_RenderAtEndOfFormTagHelper;
        #pragma warning disable 1998
        public async override global::System.Threading.Tasks.Task ExecuteAsync()
        {
#nullable restore
#line 4 "F:\DeIdWeb\數位部\資安院\deidweb_v2_k\DeIdWeb_V2_K\Views\Dept\DeptList.cshtml"
  
    ViewData["Title"] = "DeptList";
    Layout = "~/Views/Shared/_Layout.cshtml";

#line default
#line hidden
#nullable disable
            WriteLiteral("<section class=\"inside member_list\">\r\n    <div class=\"container\">\r\n        <h4 class=\"title\">單位管理</h4>\r\n        <div class=\"col-sm-12\">\r\n            ");
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("form", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "a521ff081e75de8d7c53c73385bc83b44fa244e65629", async() => {
                WriteLiteral("\r\n");
                WriteLiteral("                <!--i.fa.fa-search-->\r\n            ");
            }
            );
            __Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.FormTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper);
            __Microsoft_AspNetCore_Mvc_TagHelpers_RenderAtEndOfFormTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.RenderAtEndOfFormTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_RenderAtEndOfFormTagHelper);
            __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_0);
            await __tagHelperRunner.RunAsync(__tagHelperExecutionContext);
            if (!__tagHelperExecutionContext.Output.IsContentModified)
            {
                await __tagHelperExecutionContext.SetOutputContentAsync();
            }
            Write(__tagHelperExecutionContext.Output);
            __tagHelperExecutionContext = __tagHelperScopeManager.End();
            WriteLiteral(@"
            <button class=""btn btn_mbs"" id=""new_dept"">新增單位</button>
            <div class=""modal"" id=""dept"">
                <div class=""textarea"">
                    <div class=""close"" id=""dept_close"">✖</div>
                    <h4 class=""title"">新增單位</h4>

                    ");
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("form", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "a521ff081e75de8d7c53c73385bc83b44fa244e67333", async() => {
                WriteLiteral(@"
                        <input id=""csrf_token"" name=""csrf_token"" type=""hidden"" value=""IjY1NTQzYzJjNWEwMzBlYWU5YmZjY2RiMTM5ZWZiNDg3ZTFhM2QxMWIi.DVv-gw.lB3kAc8_kwJv6Z2L-_mlgExWIcA"">
                        <div class=""form-group required"">
                            <label class=""control-label"">單位名稱</label>
                            <input class=""form-control"" id=""a_id"">
                        </div>
                        <input class=""btn btn-default"" id=""submit_new_member"" name=""submit"" type=""submit"" value=""確定"" onclick=""adddept(); return false;"">
                    ");
            }
            );
            __Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.FormTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper);
            __Microsoft_AspNetCore_Mvc_TagHelpers_RenderAtEndOfFormTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.RenderAtEndOfFormTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_RenderAtEndOfFormTagHelper);
            __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_1);
            __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_2);
            __Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper.Method = (string)__tagHelperAttribute_3.Value;
            __tagHelperExecutionContext.AddTagHelperAttribute(__tagHelperAttribute_3);
            __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_4);
            await __tagHelperRunner.RunAsync(__tagHelperExecutionContext);
            if (!__tagHelperExecutionContext.Output.IsContentModified)
            {
                await __tagHelperExecutionContext.SetOutputContentAsync();
            }
            Write(__tagHelperExecutionContext.Output);
            __tagHelperExecutionContext = __tagHelperScopeManager.End();
            WriteLiteral(@"
                </div>
            </div>
        </div>
        <div class=""col-sm-12"">
            <table class=""table table-hover"" id=""member_active"">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>單位</th>
                        <th>建立日期</th>
                        <th>修改日期</th>
                        <th>刪除</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    <label id=""memberlst"" style=""display:none"">");
#nullable restore
#line 48 "F:\DeIdWeb\數位部\資安院\deidweb_v2_k\DeIdWeb_V2_K\Views\Dept\DeptList.cshtml"
                                          Write(ViewData["memberlist"]);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</label>

</section>
<script>
    var dept_modal = document.getElementById('dept');
    var new_dept_btn = document.getElementById(""new_dept"");
    var dept_close_span = document.getElementById(""dept_close"");

    new_dept_btn.onclick = function () {
        dept_modal.style.display = ""block"";
    }

    dept_close_span.onclick = function () {
        dept_modal.style.display = ""none"";
    }

    var lstmember = $('#memberlst').text();
    $(""#member_active"").append(lstmember);
</script>
<script>
    function adddept() {
        var dept_name = $('#a_id').val();
       //alert(dept_name);
        if (dept_name == """") {
            alert('單位名稱不可重複');
            return;
        }

        $.ajax({
            type: ""get"",
            url: ""/api/WebAPI/AddDept"",
            contentType: ""application/json"",
            async: false,
            data: {
                deptname: dept_name
            },
            success: function (response) {
                if (response ==");
            WriteLiteral(@" ""-2"") {
                    alert('名稱重複!');
                    return false;
                }
                else if (response == ""1"") {
                    //alert('2');
                    //var member_modal = document.getElementById('member');
                    //member_modal.style.display = ""none"";
                    location.reload();
                }
                else {
                    alert('新增失敗');
                    return false;
                }
                
				},
            error: function (response) {
                alert(response);
            }
        });
    }

    function deldept(depid) {

        if (confirm('請確認是否要刪除單位!')) {
            $.ajax({
                type: ""get"",
                url: ""/api/WebAPI/delDept"",
                contentType: ""application/json"",
                data: { depid: depid },
                success: function (response) {
                    if (response == 1) {
                        alert('刪除成功!');
   ");
            WriteLiteral(@"                     location.reload();
                    }
                    else if (response == -1) {
                        alert('目前此群組尚有使用者，無法刪除!!');
                        return;
                    }
                    else {
                        alert('刪除失敗!');
                    }
                },
                error: function (response) {
                    alert('刪除失敗!');
                }
            });
        }
        else {
            return;
        }
    }
</script>
");
        }
        #pragma warning restore 1998
        [global::Microsoft.AspNetCore.Mvc.Razor.Internal.RazorInjectAttribute]
        public ILocalizer localizer { get; private set; }
        [global::Microsoft.AspNetCore.Mvc.Razor.Internal.RazorInjectAttribute]
        public global::Microsoft.AspNetCore.Mvc.ViewFeatures.IModelExpressionProvider ModelExpressionProvider { get; private set; }
        [global::Microsoft.AspNetCore.Mvc.Razor.Internal.RazorInjectAttribute]
        public global::Microsoft.AspNetCore.Mvc.IUrlHelper Url { get; private set; }
        [global::Microsoft.AspNetCore.Mvc.Razor.Internal.RazorInjectAttribute]
        public global::Microsoft.AspNetCore.Mvc.IViewComponentHelper Component { get; private set; }
        [global::Microsoft.AspNetCore.Mvc.Razor.Internal.RazorInjectAttribute]
        public global::Microsoft.AspNetCore.Mvc.Rendering.IJsonHelper Json { get; private set; }
        [global::Microsoft.AspNetCore.Mvc.Razor.Internal.RazorInjectAttribute]
        public global::Microsoft.AspNetCore.Mvc.Rendering.IHtmlHelper<dynamic> Html { get; private set; }
    }
}
#pragma warning restore 1591
