#pragma checksum "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Group\GroupList.cshtml" "{ff1816ec-aa5e-4d10-87f7-6f4963833460}" "57c91da9ced3677739007a8f5d0f5016a96a44e1"
// <auto-generated/>
#pragma warning disable 1591
[assembly: global::Microsoft.AspNetCore.Razor.Hosting.RazorCompiledItemAttribute(typeof(AspNetCore.Views_Group_GroupList), @"mvc.1.0.view", @"/Views/Group/GroupList.cshtml")]
[assembly:global::Microsoft.AspNetCore.Mvc.Razor.Compilation.RazorViewAttribute(@"/Views/Group/GroupList.cshtml", typeof(AspNetCore.Views_Group_GroupList))]
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
#line 1 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\_ViewImports.cshtml"
using DeIdWeb;

#line default
#line hidden
#line 2 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\_ViewImports.cshtml"
using DeIdWeb.Models;

#line default
#line hidden
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"57c91da9ced3677739007a8f5d0f5016a96a44e1", @"/Views/Group/GroupList.cshtml")]
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"e0ea9701343602d68eda9a80005fe261fbee6a2e", @"/Views/_ViewImports.cshtml")]
    public class Views_Group_GroupList : global::Microsoft.AspNetCore.Mvc.Razor.RazorPage<dynamic>
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
            BeginContext(0, 2, true);
            WriteLiteral("\r\n");
            EndContext();
#line 2 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Group\GroupList.cshtml"
  
    ViewData["Title"] = "GroupList";
    Layout = "~/Views/Shared/_Layout.cshtml";

#line default
#line hidden
            BeginContext(94, 149, true);
            WriteLiteral("<section class=\"inside member_list\">\r\n    <div class=\"container\">\r\n        <h4 class=\"title\">群組管理</h4>\r\n        <div class=\"col-sm-12\">\r\n            ");
            EndContext();
            BeginContext(243, 199, false);
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("form", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "57c91da9ced3677739007a8f5d0f5016a96a44e15483", async() => {
                BeginContext(269, 166, true);
                WriteLiteral("\r\n                <input type=\"text\" placeholder=\"輸入關鍵字\"><a class=\"search-button\" href=\"javascript:void(0);\"></a>\r\n                <!--i.fa.fa-search-->\r\n            ");
                EndContext();
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
            EndContext();
            BeginContext(442, 289, true);
            WriteLiteral(@"
            <button class=""btn btn_mbs"" id=""new_dept"">新增群組</button>
            <div class=""modal"" id=""dept"">
                <div class=""textarea"">
                    <div class=""close"" id=""dept_close"">✖</div>
                    <h4 class=""title"">新增群組</h4>

                    ");
            EndContext();
            BeginContext(731, 634, false);
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("form", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "57c91da9ced3677739007a8f5d0f5016a96a44e17494", async() => {
                BeginContext(786, 572, true);
                WriteLiteral(@"
                        <input id=""csrf_token"" name=""csrf_token"" type=""hidden"" value=""IjY1NTQzYzJjNWEwMzBlYWU5YmZjY2RiMTM5ZWZiNDg3ZTFhM2QxMWIi.DVv-gw.lB3kAc8_kwJv6Z2L-_mlgExWIcA"">
                        <div class=""form-group required"">
                            <label class=""control-label"">單位名稱</label>
                            <input class=""form-control"" id=""a_id"">
                        </div>
                        <input class=""btn btn-default"" id=""submit_new_member"" name=""submit"" type=""submit"" value=""確定"" onclick=""adddept()"">
                    ");
                EndContext();
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
            EndContext();
            BeginContext(1365, 584, true);
            WriteLiteral(@"
                </div>
            </div>
        </div>
        <div class=""col-sm-12"">
            <table class=""table table-hover"" id=""member_active"">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>群組</th>
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
            EndContext();
            BeginContext(1950, 22, false);
#line 46 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Group\GroupList.cshtml"
                                          Write(ViewData["memberlist"]);

#line default
#line hidden
            EndContext();
            BeginContext(1972, 3571, true);
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
        //$.ajax({
        //    type: ""get"",
        //    url: ""/api/WebAPI/AddDept"",
        //    contentType: ""application/json"",
        //    data: {
        //        deptname: dept_name
        //    },
        //    success: function (status) {
        //        if (status == 1) {
        ");
            WriteLiteral(@"//            //頁面重整
        //            var dept_modal = document.getElementById('dept');
        //            dept_modal.style.display = ""none"";
        //            location.reload();
        //        }
        //        else if (status == -1) {
        //            alert('新增失敗');
        //            return;
        //        }
        //        else if (status == -2) {
        //            alert('單位名稱重複');
        //            return;
        //        }
        //        else {
        //            alert('新增失敗!');
        //            return;
        //        }
        //    },
        //    error: function (data, status) {

        //    }
        //});
        $.ajax({
            type: ""get"",
            url: ""/api/WebAPI/AddDept"",
            contentType: ""application/json"",
            async: false,
            data: {
                deptname: dept_name
            },
            success: function (response) {
                if (response == ""-2"") {
    ");
            WriteLiteral(@"                alert('名稱重複!');
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

        if (confirm('請確認是否要刪除群組!')) {
            $.ajax({
                type: ""get"",
                url: ""/api/WebAPI/delDept"",
                contentType: ""application/json"",
                data: { depid: depid },
                success: function (response) {
                    if (response == 1) {
                        alert('刪除成功!');
                        location.");
            WriteLiteral(@"reload();
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
            EndContext();
        }
        #pragma warning restore 1998
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