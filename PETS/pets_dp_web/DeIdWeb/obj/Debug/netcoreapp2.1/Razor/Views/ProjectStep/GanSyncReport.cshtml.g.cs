#pragma checksum "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml" "{ff1816ec-aa5e-4d10-87f7-6f4963833460}" "4e3b481a321270554381e2a53836d65c9bed27e0"
// <auto-generated/>
#pragma warning disable 1591
[assembly: global::Microsoft.AspNetCore.Razor.Hosting.RazorCompiledItemAttribute(typeof(AspNetCore.Views_ProjectStep_GanSyncReport), @"mvc.1.0.view", @"/Views/ProjectStep/GanSyncReport.cshtml")]
[assembly:global::Microsoft.AspNetCore.Mvc.Razor.Compilation.RazorViewAttribute(@"/Views/ProjectStep/GanSyncReport.cshtml", typeof(AspNetCore.Views_ProjectStep_GanSyncReport))]
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
#line 2 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
using System.Globalization;

#line default
#line hidden
#line 3 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
using Resources;

#line default
#line hidden
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"4e3b481a321270554381e2a53836d65c9bed27e0", @"/Views/ProjectStep/GanSyncReport.cshtml")]
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"e0ea9701343602d68eda9a80005fe261fbee6a2e", @"/Views/_ViewImports.cshtml")]
    public class Views_ProjectStep_GanSyncReport : global::Microsoft.AspNetCore.Mvc.Razor.RazorPage<IEnumerable<ProjectSampleDBData>>
    {
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_0 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("value", "1", global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_1 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("value", "2", global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
        private static readonly global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute __tagHelperAttribute_2 = new global::Microsoft.AspNetCore.Razor.TagHelpers.TagHelperAttribute("value", "3", global::Microsoft.AspNetCore.Razor.TagHelpers.HtmlAttributeValueStyle.DoubleQuotes);
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
        private global::Microsoft.AspNetCore.Mvc.TagHelpers.OptionTagHelper __Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper;
        #pragma warning disable 1998
        public async override global::System.Threading.Tasks.Task ExecuteAsync()
        {
#line 5 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
  
    ViewData["Title"] = "GanSyncReport";
    Layout = "~/Views/Shared/_Layout.cshtml";

#line default
#line hidden
            BeginContext(214, 133, true);
            WriteLiteral("\r\n<section class=\"section_top\">\r\n    <div class=\"container\">\r\n        <ul class=\"bread_crumb\">\r\n            <!-- <li>\r\n\r\n            ");
            EndContext();
            BeginContext(348, 68, false);
#line 15 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
       Write(Html.ActionLink(localizer.Text.project_list, "ProjectIndex", "Home"));

#line default
#line hidden
            EndContext();
            BeginContext(416, 64, true);
            WriteLiteral("\r\n            </li>\r\n            <li>\r\n                <a href=\"");
            EndContext();
            BeginContext(481, 162, false);
#line 18 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                    Write(Url.Action("GanSyncReport", "ProjectStep", new { proj_id = ViewData["ProjectId"], project_name = ViewData["ProjectName"], project_cht = ViewData["Project_Cht"] }));

#line default
#line hidden
            EndContext();
            BeginContext(643, 2, true);
            WriteLiteral("\">");
            EndContext();
            BeginContext(646, 23, false);
#line 18 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                                                                                                                                                                         Write(ViewData["Project_Cht"]);

#line default
#line hidden
            EndContext();
            BeginContext(669, 313, true);
            WriteLiteral(@"</a>
            </li> -->
        </ul>
    </div>
</section>
<section class=""project_wrapper"">
    <div class=""container"">
        <div class=""row"">
            <div class=""col-sm-12"">
                <div class=""col-sm-3"">
                    <div class=""project_title"">
                        <h4>");
            EndContext();
            BeginContext(983, 23, false);
#line 29 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                       Write(ViewData["Project_Cht"]);

#line default
#line hidden
            EndContext();
            BeginContext(1006, 337, true);
            WriteLiteral(@"</h4>
                    </div>
                    <div class=""status_bar"">
                        <h4 class=""method"">資料差分隱私流程</h4>
                        <div class=""status"">
                            <div class=""status_no_line active"">
                                <h6>欄位選擇及屬性判定</h6>
                                <p>");
            EndContext();
            BeginContext(1344, 30, false);
#line 36 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                              Write(localizer.Text.step2_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(1374, 307, true);
            WriteLiteral(@"</p>
                                <h3>1</h3>
                            </div>
                        </div>

                        <div class=""status"">
                            <div class=""status_notnow"">
                                <h6>關聯欄位設定</h6>
                                <p>");
            EndContext();
            BeginContext(1682, 30, false);
#line 44 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                              Write(localizer.Text.step4_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(1712, 306, true);
            WriteLiteral(@"</p>
                                <h3>2</h3>
                            </div>
                        </div>

                        <div class=""status"">
                            <div class=""status_notnow"">
                                <h6>資料可用性</h6>
                                <p>");
            EndContext();
            BeginContext(2019, 30, false);
#line 52 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                              Write(localizer.Text.step6_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(2049, 304, true);
            WriteLiteral(@"</p>
                                <h3>3</h3>
                            </div>
                        </div>
                        <div class=""status"">
                            <div class=""status_notnow"">
                                <h6>報表與產出</h6>
                                <p>");
            EndContext();
            BeginContext(2354, 30, false);
#line 59 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                              Write(localizer.Text.step6_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(2384, 495, true);
            WriteLiteral(@"</p>
                                <h3>4</h3>
                            </div>
                        </div>
                    </div>
                </div>
                <div class=""col-sm-9"">
                    <h4 class=""title"">報表產生與資料匯出<span class=""step_inf"">*請選擇隱私強化程度</span></h4>
                    <h2 class=""p_relative"">
                        <strong>隱私層級</strong>
                        <select class=""form-control"" id=""PL-options"">
                            ");
            EndContext();
            BeginContext(2879, 30, false);
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("option", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "4e3b481a321270554381e2a53836d65c9bed27e010094", async() => {
                BeginContext(2897, 3, true);
                WriteLiteral("LV1");
                EndContext();
            }
            );
            __Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.OptionTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper);
            __Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper.Value = (string)__tagHelperAttribute_0.Value;
            __tagHelperExecutionContext.AddTagHelperAttribute(__tagHelperAttribute_0);
            await __tagHelperRunner.RunAsync(__tagHelperExecutionContext);
            if (!__tagHelperExecutionContext.Output.IsContentModified)
            {
                await __tagHelperExecutionContext.SetOutputContentAsync();
            }
            Write(__tagHelperExecutionContext.Output);
            __tagHelperExecutionContext = __tagHelperScopeManager.End();
            EndContext();
            BeginContext(2909, 30, true);
            WriteLiteral("\r\n                            ");
            EndContext();
            BeginContext(2939, 30, false);
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("option", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "4e3b481a321270554381e2a53836d65c9bed27e011497", async() => {
                BeginContext(2957, 3, true);
                WriteLiteral("LV2");
                EndContext();
            }
            );
            __Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.OptionTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper);
            __Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper.Value = (string)__tagHelperAttribute_1.Value;
            __tagHelperExecutionContext.AddTagHelperAttribute(__tagHelperAttribute_1);
            await __tagHelperRunner.RunAsync(__tagHelperExecutionContext);
            if (!__tagHelperExecutionContext.Output.IsContentModified)
            {
                await __tagHelperExecutionContext.SetOutputContentAsync();
            }
            Write(__tagHelperExecutionContext.Output);
            __tagHelperExecutionContext = __tagHelperScopeManager.End();
            EndContext();
            BeginContext(2969, 30, true);
            WriteLiteral("\r\n                            ");
            EndContext();
            BeginContext(2999, 30, false);
            __tagHelperExecutionContext = __tagHelperScopeManager.Begin("option", global::Microsoft.AspNetCore.Razor.TagHelpers.TagMode.StartTagAndEndTag, "4e3b481a321270554381e2a53836d65c9bed27e012900", async() => {
                BeginContext(3017, 3, true);
                WriteLiteral("LV3");
                EndContext();
            }
            );
            __Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper = CreateTagHelper<global::Microsoft.AspNetCore.Mvc.TagHelpers.OptionTagHelper>();
            __tagHelperExecutionContext.Add(__Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper);
            __Microsoft_AspNetCore_Mvc_TagHelpers_OptionTagHelper.Value = (string)__tagHelperAttribute_2.Value;
            __tagHelperExecutionContext.AddTagHelperAttribute(__tagHelperAttribute_2);
            await __tagHelperRunner.RunAsync(__tagHelperExecutionContext);
            if (!__tagHelperExecutionContext.Output.IsContentModified)
            {
                await __tagHelperExecutionContext.SetOutputContentAsync();
            }
            Write(__tagHelperExecutionContext.Output);
            __tagHelperExecutionContext = __tagHelperScopeManager.End();
            EndContext();
            BeginContext(3029, 2, true);
            WriteLiteral("\r\n");
            EndContext();
            BeginContext(3095, 305, true);
            WriteLiteral(@"                            <!-- <option value=""5"">LV5</option> -->
                        </select>
                    </h2>
                    <table class=""table table-hover  table-bordered"">
                        <caption>table </caption>
                        <thead class=""thead-inverse""");
            EndContext();
            BeginWriteAttribute("style", " style=\"", 3400, "\"", 3408, 0);
            EndWriteAttribute();
            BeginContext(3409, 1426, true);
            WriteLiteral(@">
                            <tr>
                                <th class=""text-center"">隱私強化程度</th>
                                <th class=""text-center"">資料可用性</th>
                                <th class=""text-center""></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class=""text-center""><strong>LV1</strong></td>
                                <td class=""text-center"">高</td>
                                <td><div class=""circle"" style=""background:green""></div></td>
                            </tr>
                            <tr>
                                <td class=""text-center""><strong>LV2</strong></td>
                                <td class=""text-center"">中</td>
                                <td><div class=""circle"" style=""background:yellow""></div></td>
                            </tr>
                            <tr>
                              ");
            WriteLiteral(@"  <td class=""text-center""><strong>LV3</strong></td>
                                <td class=""text-center"">低</td>
                                <td><div class=""circle"" style=""background:orange""></div></td>
                            </tr>
                         
                        </tbody>
                    </table>
                    <label id=""returnurl"" style=""display: none"">");
            EndContext();
            BeginContext(4836, 21, false);
#line 105 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                                           Write(ViewData["returnurl"]);

#line default
#line hidden
            EndContext();
            BeginContext(4857, 74, true);
            WriteLiteral("</label>\r\n                    <label id=\"loginname\" style=\"display: none\">");
            EndContext();
            BeginContext(4932, 21, false);
#line 106 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                                           Write(ViewData["loginname"]);

#line default
#line hidden
            EndContext();
            BeginContext(4953, 141, true);
            WriteLiteral("</label>\r\n                    \r\n                    <div class=\"btn btn_mbs btn_next\" onclick=\"exportFile()\">\r\n                        匯出資料\r\n");
            EndContext();
            BeginContext(5390, 1405, true);
            WriteLiteral(@"
                    </div>
                </div>
            </div>
        </div>
					<!--資料無誤，成功-->
                    <div class=""modal fade"" id=""lessThanThree"" tabindex=""-1"" role=""dialog"" aria-labelledby=""exampleModalCenterTitle"" aria-hidden=""true"">
                        <div class=""modal-dialog modal-dialog-centered"" role=""document"">
                            <div class=""modal-content"">
                                <div class=""modal-header"">
                                    <h4 class=""modal-title"" id=""exampleModalLongTitle"">資料生成</h4>
                                </div>
                                <div class=""modal-body"">
                                    資料匯出中，依資料大小不同需花費數分鐘到數小時不等，完成後將以狀態通知。
                                </div>
                                <div class=""modal-footer"">
                                    <button type=""button"" class=""btn btn_mbs"" data-dismiss=""modal"" onclick=""returntopage()"">確定</button>
                                </div>
     ");
            WriteLiteral(@"                       </div>
                        </div>
                    </div>
				
					<!--資料檢查中動畫-->
                    <div class=""modal fade"" id=""datachecking"" tabindex=""-1"" role=""dialog"" aria-labelledby=""exampleModalCenterTitle"" aria-hidden=""true"" >
                        <svg id=""dc-spinner"" version=""1.1"" xmlns=""http://www.w3.org/2000/svg"" x=""0px"" y=""0px""");
            EndContext();
            BeginWriteAttribute("width:\"38", " width:\"38=\"", 6795, "\"", 6807, 0);
            EndWriteAttribute();
            BeginWriteAttribute("height:\"38", " height:\"38=\"", 6808, "\"", 6821, 0);
            EndWriteAttribute();
            BeginContext(6822, 2155, true);
            WriteLiteral(@" viewBox=""0 0 38 38"" preserveAspectRatio=""xMinYMin meet"">
                            <text x=""14"" y=""21"" font-size=""2.5px"" style=""letter-spacing:0.2;"" fill=""grey"">
                                資料檢查中
                                <animate attributeName=""opacity"" values=""0;1;0"" dur=""1.8s"" repeatCount=""indefinite""></animate>
                            </text>
                            <path fill=""#cccccc"" d=""M20,35c-8.271,0-15-6.729-15-15S11.729,5,20,5s15,6.729,15,15S28.271,35,20,35z M20,5.203    C11.841,5.203,5.203,11.841,5.203,20c0,8.159,6.638,14.797,14.797,14.797S34.797,28.159,34.797,20    C34.797,11.841,28.159,5.203,20,5.203z""></path>
                            <path fill=""#cccccc"" d=""M20,33.125c-7.237,0-13.125-5.888-13.125-13.125S12.763,6.875,20,6.875S33.125,12.763,33.125,20    S27.237,33.125,20,33.125z M20,7.078C12.875,7.078,7.078,12.875,7.078,20c0,7.125,5.797,12.922,12.922,12.922    S32.922,27.125,32.922,20C32.922,12.875,27.125,7.078,20,7.078z""></path>
                            <path fi");
            WriteLiteral(@"ll=""#2AA198"" stroke=""#1890ff"" stroke-width=""0.6027"" stroke-miterlimit=""10"" d=""M5.203,20    c0-8.159,6.638-14.797,14.797-14.797V5C11.729,5,5,11.729,5,20s6.729,15,15,15v-0.203C11.841,34.797,5.203,28.159,5.203,20z"">
                                <animatetransform attributeName=""transform"" type=""rotate"" from=""0 20 20"" to=""360 20 20"" calcMode=""spline"" keySplines=""0.4, 0, 0.2, 1"" keyTimes=""0;1"" dur=""2s"" repeatCount=""indefinite""></animatetransform>
                            </path>
                            <path fill=""#859900"" stroke=""#C2CFFE"" stroke-width=""0.5"" stroke-miterlimit=""10"" d=""M7.078,20    c0-7.125,5.797-12.922,12.922-12.922V6.875C12.763,6.875,6.875,12.763,6.875,20S12.763,33.125,20,33.125v-0.203    C12.875,32.922,7.078,27.125,7.078,20z"">
                                <animatetransform attributeName=""transform"" type=""rotate"" from=""0 20 20"" to=""360 20 20"" dur=""1.8s"" repeatCount=""indefinite""></animatetransform>
                            </path>
                        </svg>
               ");
            WriteLiteral("     </div>\r\n                    <!--勾選資料大於三筆後進入資料檢查-->\r\n\r\n\r\n        <label id=\"pid\" style=\"display: none\">");
            EndContext();
            BeginContext(8978, 21, false);
#line 153 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                         Write(ViewData["ProjectId"]);

#line default
#line hidden
            EndContext();
            BeginContext(8999, 58, true);
            WriteLiteral("</label>\r\n        <label id=\"pname\" style=\"display: none\">");
            EndContext();
            BeginContext(9058, 23, false);
#line 154 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                           Write(ViewData["ProjectName"]);

#line default
#line hidden
            EndContext();
            BeginContext(9081, 62, true);
            WriteLiteral("</label>\r\n        <label id=\"pname_cht\" style=\"display: none\">");
            EndContext();
            BeginContext(9144, 23, false);
#line 155 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                               Write(ViewData["Project_Cht"]);

#line default
#line hidden
            EndContext();
            BeginContext(9167, 61, true);
            WriteLiteral("</label>\r\n        <label id=\"rp_count\" style=\"display: none\">");
            EndContext();
            BeginContext(9229, 20, false);
#line 156 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                              Write(ViewData["RP_Count"]);

#line default
#line hidden
            EndContext();
            BeginContext(9249, 61, true);
            WriteLiteral("</label>\r\n        <label id=\"syn_data\" style=\"display: none\">");
            EndContext();
            BeginContext(9311, 20, false);
#line 157 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                              Write(ViewData["syn_data"]);

#line default
#line hidden
            EndContext();
            BeginContext(9331, 61, true);
            WriteLiteral("</label>\r\n        <label id=\"raw_data\" style=\"display: none\">");
            EndContext();
            BeginContext(9393, 20, false);
#line 158 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                              Write(ViewData["raw_data"]);

#line default
#line hidden
            EndContext();
            BeginContext(9413, 62, true);
            WriteLiteral("</label>\r\n        <label id=\"return_url\" style=\"display:none\">");
            EndContext();
            BeginContext(9476, 21, false);
#line 159 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                               Write(ViewData["returnurl"]);

#line default
#line hidden
            EndContext();
            BeginContext(9497, 63, true);
            WriteLiteral("</label>\r\n        <label id=\"p_selectcsv\" style=\"display:none\">");
            EndContext();
            BeginContext(9561, 26, false);
#line 160 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                                Write(ViewData["select_csvdata"]);

#line default
#line hidden
            EndContext();
            BeginContext(9587, 62, true);
            WriteLiteral("</label>\r\n        <label id=\"dataexport\" style=\"display:none\">");
            EndContext();
            BeginContext(9650, 24, false);
#line 161 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                               Write(localizer.Message.export);

#line default
#line hidden
            EndContext();
            BeginContext(9674, 61, true);
            WriteLiteral("</label>\r\n        <label id=\"deiderror\" style=\"display:none\">");
            EndContext();
            BeginContext(9736, 28, false);
#line 162 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                              Write(localizer.Message.deid_error);

#line default
#line hidden
            EndContext();
            BeginContext(9764, 1299, true);
            WriteLiteral(@"</label>
    </div>
</section>
<script>
     var syn_data = $('#syn_data').text();
     var raw_data = $('#raw_data').text();
    // alert(raw_data);
     $('#tb_raw').append(raw_data);
     $('#tb_syn').append(syn_data);

</script>
<script>
    $('.tabs').click(function(event){
        let $tab = $(event.target).parent();
        $(this).find('.active').removeClass(""active"");
        $tab.addClass('active');
        let index = $tab.index();
        $("".contents .content"").siblings('.active').removeClass('active').end().eq(index).addClass(""active"");
    })

    function returnml() {
        var pname_cht = $('#pname_cht').text();
        var pname = $('#pname').text();
        var pid = $('#pid').text();
          var returnurl = $('#returnurl').text();
        var loginname = $('#loginname').text();
        $.ajax({
            type: ""get"",
            url: ""/api/WebAPI/returnMLStatus"",
            contentType: ""application/json"",
            async: false,
            data:
 ");
            WriteLiteral(@"           {
                pid: pid
            },
            success: function (response) {
                //成功

            },
            error: function (response) {
                //alert(savecolerror);
            }
        });
        location.href = """);
            EndContext();
            BeginContext(11064, 38, false);
#line 205 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                    Write(Url.Action("MLUtility", "ProjectStep"));

#line default
#line hidden
            EndContext();
            BeginContext(11102, 1151, true);
            WriteLiteral(@"/?proj_id="" + encodeURIComponent(pid) + ""&project_name="" + encodeURIComponent(pname) + ""&project_cht="" + encodeURIComponent(pname_cht) + ""&loginname="" + encodeURIComponent(loginname) + ""&returnurl="" + encodeURIComponent(returnurl);

    }
</script>
<script>
    function exportFile()
    {
        //input json: {'projID': '123', 'userID': 'JOJO', 'projName': 'adult', 'dataName' : ['synthetic_transform_rmhit3.csv']}
     var pid = $('#pid').text();;
            var pname = $('#pname').text();
        var p_selectcsv = $('#p_selectcsv').text();
           var return_url =$('#return_url').text();
            $('#datachecking').modal('show');
        $('#datachecking').modal({ backdrop: 'static', keyboard: false });
    
    $.ajax({
                    type: ""get"",
                  url: ""/api/WebAPI/ExportData"",
                    contentType: ""application/json"",
                  data:
                  {
                      pid: pid, pname: pname, selectcsv: p_selectcsv
               ");
            WriteLiteral("   },\r\n        success: function (status) {\r\n            //alert(status);\r\n                        //document.location.href = \"");
            EndContext();
            BeginContext(12254, 26, false);
#line 230 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\GanSyncReport.cshtml"
                                               Write(Url.Action("Index","Home"));

#line default
#line hidden
            EndContext();
            BeginContext(12280, 811, true);
            WriteLiteral(@""";
                        if (status) {
                               $('#datachecking').modal('hide'); 
                $('#lessThanThree').modal({ backdrop: 'static', keyboard: false });
                $('#lessThanThree').modal('show'); 
                        }
                        else {
                            alert('匯出錯誤');
                            return;
                        }
                    },
                    error: function (status) {
                        alert('匯出錯誤');
                        return;
                    }

                });

    }

    function returntopage() {
         // location.href = ""/Home/ProjectIndex"";
           var return_url =$('#return_url').text();
        location.href = return_url;
    }
</script>


");
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
        public global::Microsoft.AspNetCore.Mvc.Rendering.IHtmlHelper<IEnumerable<ProjectSampleDBData>> Html { get; private set; }
    }
}
#pragma warning restore 1591