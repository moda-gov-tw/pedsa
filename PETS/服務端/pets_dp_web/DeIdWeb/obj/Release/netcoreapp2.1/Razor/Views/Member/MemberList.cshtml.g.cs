#pragma checksum "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Member\MemberList.cshtml" "{ff1816ec-aa5e-4d10-87f7-6f4963833460}" "7024c1c19a7a8debe7692f17f89645b17a625ca2"
// <auto-generated/>
#pragma warning disable 1591
[assembly: global::Microsoft.AspNetCore.Razor.Hosting.RazorCompiledItemAttribute(typeof(AspNetCore.Views_Member_MemberList), @"mvc.1.0.view", @"/Views/Member/MemberList.cshtml")]
[assembly:global::Microsoft.AspNetCore.Mvc.Razor.Compilation.RazorViewAttribute(@"/Views/Member/MemberList.cshtml", typeof(AspNetCore.Views_Member_MemberList))]
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
#line 1 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Member\MemberList.cshtml"
using System.Globalization;

#line default
#line hidden
#line 2 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Member\MemberList.cshtml"
using Resources;

#line default
#line hidden
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"7024c1c19a7a8debe7692f17f89645b17a625ca2", @"/Views/Member/MemberList.cshtml")]
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"e0ea9701343602d68eda9a80005fe261fbee6a2e", @"/Views/_ViewImports.cshtml")]
    public class Views_Member_MemberList : global::Microsoft.AspNetCore.Mvc.Razor.RazorPage<dynamic>
    {
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_0 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("class", new global::Microsoft.AspNetCore.Html.HtmlString("search_form"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_1 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("class", new global::Microsoft.AspNetCore.Html.HtmlString("form-control"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_2 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("id", new global::Microsoft.AspNetCore.Html.HtmlString("deptlist"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_3 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("name", "powner", global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_4 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("class", new global::Microsoft.AspNetCore.Html.HtmlString("form"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_5 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("action", new global::Microsoft.AspNetCore.Html.HtmlString(""), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_6 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("method", "post", global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_7 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("role", new global::Microsoft.AspNetCore.Html.HtmlString("form"), global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
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
        private global::Microsoft.AspNetCore.Mvc.TagHelpers.SelectTagHelper __Microsoft_AspNetCore_Mvc_TagHelpers_SelectTagHelper;
        #pragma warning disable 1998
        public async override global::System.Threading.Tasks.Task ExecuteAsync()
        {
#line 4 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Member\MemberList.cshtml"
  
    ViewData["Title"] = "MemberList";
    Layout = "~/Views/Shared/_Layout.cshtml";

#line default
#line hidden
            BeginContext(170, 149, true);
            WriteLiteral("<section class=\"inside member_list\">\r\n    <div class=\"container\">\r\n        <h4 class=\"title\">人員管理</h4>\r\n        <div class=\"col-sm-12\">\r\n            ");
            EndContext();
            BeginContext(319, 199, false);
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("form", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "7024c1c19a7a8debe7692f17f89645b17a625ca26779", async() => {
                BeginContext(345, 166, true);
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
            BeginContext(518, 339, true);
            WriteLiteral(@"
            <button class=""btn btn_mbs"" id=""new_member"">新增人員</button>
            <div class=""modal"" id=""member"">
                <div class=""textarea"">
                    <div class=""close"" id=""member_close"">✖</div>
                    <h4 class=""title"">新增人員</h4>
                    <p>確認新增後將寄送臨時密碼給該使用者</p>
                    ");
            EndContext();
            BeginContext(857, 1456, false);
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("form", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "7024c1c19a7a8debe7692f17f89645b17a625ca28841", async() => {
                BeginContext(912, 681, true);
                WriteLiteral(@"
                        <input id=""csrf_token"" name=""csrf_token"" type=""hidden"" value=""IjY1NTQzYzJjNWEwMzBlYWU5YmZjY2RiMTM5ZWZiNDg3ZTFhM2QxMWIi.DVv-gw.lB3kAc8_kwJv6Z2L-_mlgExWIcA"">
                        <div class=""form-group required"">
                            <label class=""control-label"">User ID</label>
                            <input class=""form-control"" id=""useraccount"">
                        </div>
                        <div class=""form-group required"">
                            <label class=""control-label"">User Password</label>
                            <input class=""form-control"" id=""userpwd"" type=""password"">
                        </div>
");
                EndContext();
                BeginContext(1784, 156, true);
                WriteLiteral("                        <div class=\"form-group required\">\r\n                            <label class=\"control-label\">單位</label>\r\n                            ");
                EndContext();
                BeginContext(1940, 173, false);
                __tagHelperExecutionContext = __tagHelperScopeManager.Begin("select", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "7024c1c19a7a8debe7692f17f89645b17a625ca210208", async() => {
                }
                );
                __Microsoft_AspNetCore_Mvc_TagHelpers_SelectTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.SelectTagHelper>();
                __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_SelectTagHelper);
                __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_1);
                __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_2);
                __Microsoft_AspNetCore_Mvc_TagHelpers_SelectTagHelper.Name = (string)__tagHelperAttribute_3.Value;
                __tagHelperExecutionContext.AddTagHelperAttribute(__tagHelperAttribute_3);
#line 39 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Member\MemberList.cshtml"
__Microsoft_AspNetCore_Mvc_TagHelpers_SelectTagHelper.Items = (new SelectList(@ViewBag.listmember, "Id", "dept_name"));

#line default
#line hidden
                __tagHelperExecutionContext.AddTagHelperAttribute("asp-items", __Microsoft_AspNetCore_Mvc_TagHelpers_SelectTagHelper.Items, global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
                await __tagHelperRunner.RunAsync(__tagHelperExecutionContext);
                if (!__tagHelperExecutionContext.Output.IsContentModified)
                {
                    await __tagHelperExecutionContext.SetOutputContentAsync();
                }
                Write(__tagHelperExecutionContext.Output);
                __tagHelperExecutionContext = __tagHelperScopeManager.End();
                EndContext();
                BeginContext(2113, 193, true);
                WriteLiteral("\r\n                        </div>\r\n                        <input class=\"btn btn-default\" id=\"submit_new_member\" name=\"submit\" type=\"submit\" value=\"確定\" onclick=\"AddUser()\">\r\n                    ");
                EndContext();
            }
            );
            __Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.FormTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper);
            __Microsoft_AspNetCore_Mvc_TagHelpers_RenderAtEndOfFormTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.RenderAtEndOfFormTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_RenderAtEndOfFormTagHelper);
            __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_4);
            __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_5);
            __Microsoft_AspNetCore_Mvc_TagHelpers_FormTagHelper.Method = (string)__tagHelperAttribute_6.Value;
            __tagHelperExecutionContext.AddTagHelperAttribute(__tagHelperAttribute_6);
            __tagHelperExecutionContext.AddHtmlAttribute(__tagHelperAttribute_7);
            await __tagHelperRunner.RunAsync(__tagHelperExecutionContext);
            if (!__tagHelperExecutionContext.Output.IsContentModified)
            {
                await __tagHelperExecutionContext.SetOutputContentAsync();
            }
            Write(__tagHelperExecutionContext.Output);
            __tagHelperExecutionContext = __tagHelperScopeManager.End();
            EndContext();
            BeginContext(2313, 582, true);
            WriteLiteral(@"
                </div>
            </div>
        </div>
        <div class=""col-sm-12"">
            <table class=""table table-hover"" id=""member_active"">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>姓名</th>
                        <th>單位</th>
                        <th>建立時間</th>
                        <th>刪除</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    <label id=""memberlst"" style=""display:none"">");
            EndContext();
            BeginContext(2896, 22, false);
#line 61 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\Member\MemberList.cshtml"
                                          Write(ViewData["memberlist"]);

#line default
#line hidden
            EndContext();
            BeginContext(2918, 2473, true);
            WriteLiteral(@"</label>

</section>
<script>
    var member_modal = document.getElementById('member');
    var new_member_btn = document.getElementById(""new_member"");
    var member_close_span = document.getElementById(""member_close"");

    new_member_btn.onclick = function () {
        member_modal.style.display = ""block"";
    }

    member_close_span.onclick = function () {
        member_modal.style.display = ""none"";
    }

    var lstmember = $('#memberlst').text();
    $(""#member_active"").append(lstmember);
    
</script>
<script>
    function delmember(uid) {
        if (confirm('請確認是否要刪除使用者!')) {
            $.ajax({
                type: ""get"",
                url: ""/api/WebAPI/delUser"",
                contentType: ""application/json"",
                data: { usrid: uid },
                success: function (status) {
                    alert('刪除成功!');
                    location.reload();
                },
                error: function (status) {
                    alert('刪除失敗!");
            WriteLiteral(@"');
                }
            });
        }
        else {
            return;
        }
    }

    function AddUser() {
        var usracc = $(""#useraccount"").val();
        var usrpwd = $(""#userpwd"").val();
        // var pinput = $(""#p_input"").val();
        //var poutput = $(""#p_output"").val();
        var userdept = $(""#deptlist option:selected"").val();
        if (usracc == """") {
            alert('請輸入帳號名稱');
            return false;
        }

        if (userdept == 0) {
            alert('請選擇帳號所屬單位!');
            return false;

        }
        $.ajax({
				type: ""get"",
            url: ""/api/WebAPI/AddMember"",
				contentType: ""application/json"",
				async: false,
				     data: {
                usracc: usracc,
                usrpwd: usrpwd,
                userdept: userdept
            },
            success: function (response) {
                if (response == ""-5"") {
                    alert('帳號名稱重複!');
                    return false;
         ");
            WriteLiteral(@"       }
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
					//alert(response);
");
            EndContext();
            BeginContext(5533, 1337, true);
            WriteLiteral(@"
				},
				error: function (response) {
                    alert(response);
				}
			});
        //$.ajax({
        //    type: ""get"",
        //    url: ""/api/WebAPI/AddMember"",
        //    contentType: ""application/json"",
        //    data: {
        //        usracc: usracc,
        //        usrpwd: usrpwd,
        //        userdept: userdept
        //    },
        //    success: function (response) {
        //        // alert('project load success');
        //        alert('111');
        //        alert(response);
        //        //alert(data);
        //        //    $(""#projectlist"").html(data);
        //        if (response == ""-2"") {
        //            alert('帳號名稱重複!');
        //            return false;
        //        }
        //        else if (response == ""1"") {
        //            alert('2');
        //            var member_modal = document.getElementById('member');
        //            member_modal.style.display = ""none"";
        //         ");
            WriteLiteral(@"   location.reload();
        //        }
        //        else {
        //            alert('新增失敗');
        //            return false;
        //        }
        //    },
        //    error: function (response) {
        //        alert('Error');
        //    }

        //});
    }
</script>");
            EndContext();
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
