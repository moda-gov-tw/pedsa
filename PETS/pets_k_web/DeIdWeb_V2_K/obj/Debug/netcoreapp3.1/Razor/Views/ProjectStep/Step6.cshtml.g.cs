#pragma checksum "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml" "{ff1816ec-aa5e-4d10-87f7-6f4963833460}" "e4ff5a184714e733efc00ebfbb9d3c139c90e1d9"
// <auto-generated/>
#pragma warning disable 1591
[assembly: global::Microsoft.AspNetCore.Razor.Hosting.RazorCompiledItemAttribute(typeof(AspNetCore.Views_ProjectStep_Step6), @"mvc.1.0.view", @"/Views/ProjectStep/Step6.cshtml")]
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
#line 1 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\_ViewImports.cshtml"
using DeIdWeb_V2_K;

#line default
#line hidden
#nullable disable
#nullable restore
#line 2 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\_ViewImports.cshtml"
using DeIdWeb_V2_K.Models;

#line default
#line hidden
#nullable disable
#nullable restore
#line 2 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
using System.Globalization;

#line default
#line hidden
#nullable disable
#nullable restore
#line 3 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
using Resources;

#line default
#line hidden
#nullable disable
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"e4ff5a184714e733efc00ebfbb9d3c139c90e1d9", @"/Views/ProjectStep/Step6.cshtml")]
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"f7e853e99b4cd50ed2f7f7df1acd9abe40c6c468", @"/Views/_ViewImports.cshtml")]
    public class Views_ProjectStep_Step6 : global::Microsoft.AspNetCore.Mvc.Razor.RazorPage<IEnumerable<ProjectSampleDBData>>
    {
        #pragma warning disable 1998
        public async override global::System.Threading.Tasks.Task ExecuteAsync()
        {
#nullable restore
#line 5 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
  
    ViewData["Title"] = "Step6";
    Layout = "~/Views/Shared/_Layout.cshtml";

#line default
#line hidden
#nullable disable
            WriteLiteral("\r\n<section class=\"section_top\">\r\n    <div class=\"container\">\r\n        <ul class=\"bread_crumb\">\r\n            <!-- <li>\r\n            ");
#nullable restore
#line 14 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
       Write(Html.ActionLink(localizer.Text.project_list, "ProjectIndex", "Home"));

#line default
#line hidden
#nullable disable
            WriteLiteral("\r\n            </li>\r\n            <li>\r\n                <a href=\"");
#nullable restore
#line 17 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                    Write(Url.Action("Step6", "ProjectStep", new { proj_id = ViewData["ProjectId"], project_name = ViewData["ProjectName"], project_cht = ViewData["Project_Cht"] }));

#line default
#line hidden
#nullable disable
            WriteLiteral("\">");
#nullable restore
#line 17 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                                                                                                                                                 Write(ViewData["Project_Cht"]);

#line default
#line hidden
#nullable disable
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
#nullable restore
#line 28 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                       Write(ViewData["Project_Cht"]);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</h4>
                    </div>
                    <div class=""status_bar"">
                        <h4 class=""method"">K匿名隱私強化流程</h4>
                        <div class=""status"">
                            <div class=""status_no_line"">
                                <h6>");
#nullable restore
#line 34 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                               Write(localizer.Text.step2);

#line default
#line hidden
#nullable disable
            WriteLiteral("</h6>\r\n                                <p>");
#nullable restore
#line 35 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                              Write(localizer.Text.step2_menu_list);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</p>
                                <h3>1</h3>
                            </div>
                        </div>
                        <div class=""status"">
                            <div class=""status_notnow"">
                                <h6>");
#nullable restore
#line 41 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                               Write(localizer.Text.step3);

#line default
#line hidden
#nullable disable
            WriteLiteral("</h6>\r\n                                <p>");
#nullable restore
#line 42 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                              Write(localizer.Text.step3_menu_list);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</p>
                                <h3>2</h3>
                            </div>
                        </div>
                        <div class=""status"">
                            <div class=""status_notnow"">
                                <h6>隱私強化處理</h6>
                                <p>");
#nullable restore
#line 49 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                              Write(localizer.Text.step4_menu_list);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</p>
                                <h3>3</h3>
                            </div>
                        </div>
                        <div class=""status"">
                            <div class=""status_notnow active"">
                                <h6>報表產生與資料匯出</h6>
                                <p>");
#nullable restore
#line 56 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                              Write(localizer.Text.step6_menu_list);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</p>
                                <h3>4</h3>
                            </div>
                        </div>
                    </div>
                </div>
                <div class=""col-sm-9"">
                    <div class=""project_content"">
                        <div class=""tab-pane step05 col-sm-12"">
                            <h4 class=""title"">資料彙整與評估</h4>
                            <h6>");
#nullable restore
#line 66 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                           Write(localizer.Text.dataset_name);

#line default
#line hidden
#nullable disable
            WriteLiteral("：");
#nullable restore
#line 66 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                        Write(ViewData["pro_tb"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</h6>\r\n");
            WriteLiteral(@"                            <table class=""table table-hover table-bordered"" id=""final_report"">
                                <thead class=""thead-dark"">
                                    <tr>
                                        <th style=""width: 108px;"">原資料筆數</th>
                                        <th style=""width: 164px;"">隱私強化後資料筆數</th>
                                        <th style=""width: 90px;"">刪除筆數</th>
                                        <th style=""width: 108px;"">刪除資料佔比</th>
                                        <th style=""width: 108px;"">風險基準值</th>

                                    </tr>
                                </thead>
                                <tbody></tbody>
                            </table>
");
            WriteLiteral("                        </div>\r\n                        <div class=\"tab-pane step05 col-sm-12\">\r\n                            <h4 class=\"title\">");
#nullable restore
#line 93 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                         Write(localizer.Text.gen_setting);

#line default
#line hidden
#nullable disable
            WriteLiteral("</h4>\r\n");
#nullable restore
#line 94 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                              
                                int rpcount = 0;
                                var rpcount_str = ViewData["RP_Count"];
                                if (rpcount_str != null)
                                {
                                    rpcount = int.Parse(rpcount_str.ToString());

                                    int x = 1;
                                    foreach (var item in Model)
                                    {
                                        string tb = "tb_" + x.ToString();

#line default
#line hidden
#nullable disable
            WriteLiteral("                                        <h6>");
#nullable restore
#line 105 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(localizer.Text.tb);

#line default
#line hidden
#nullable disable
            WriteLiteral("：");
#nullable restore
#line 105 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                          Write(item.pro_tb);

#line default
#line hidden
#nullable disable
            WriteLiteral("</h6>\r\n                                        <table class=\"table table-hover table-bordered\"");
            BeginWriteAttribute("id", " id=\"", 5257, "\"", 5265, 1);
#nullable restore
#line 106 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
WriteAttributeValue("", 5262, tb, 5262, 3, false);

#line default
#line hidden
#nullable disable
            EndWriteAttribute();
            WriteLiteral(">\r\n                                            <thead class=\"thead-dark\">\r\n                                                <tr>\r\n                                                    <th>");
#nullable restore
#line 109 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                   Write(localizer.Text.ch_col_name);

#line default
#line hidden
#nullable disable
            WriteLiteral("</th>\r\n                                                    <th>");
#nullable restore
#line 110 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                   Write(localizer.Text.data_attr);

#line default
#line hidden
#nullable disable
            WriteLiteral("</th>\r\n                                                    <th>");
#nullable restore
#line 111 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                   Write(localizer.Text.process_flow);

#line default
#line hidden
#nullable disable
            WriteLiteral("</th>\r\n                                                </tr>\r\n                                            </thead>\r\n                                            <tbody></tbody>\r\n                                        </table>\r\n");
#nullable restore
#line 116 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                        x++;
                                    }
                                }
                            

#line default
#line hidden
#nullable disable
            WriteLiteral("                        </div>\r\n                        <div class=\"tab-pane step05 col-sm-12\">\r\n                            <h4 class=\"title\">");
#nullable restore
#line 122 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                         Write(localizer.Text.warning_info);

#line default
#line hidden
#nullable disable
            WriteLiteral("</h4>\r\n");
#nullable restore
#line 123 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                              
                                int y = 1;
                                foreach (var item in Model)
                                {
                                    string tb = "warn_" + y.ToString();

#line default
#line hidden
#nullable disable
            WriteLiteral("                                    <h6>");
#nullable restore
#line 128 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                   Write(localizer.Text.dataset_name);

#line default
#line hidden
#nullable disable
            WriteLiteral("：");
#nullable restore
#line 128 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                                Write(item.pro_tb);

#line default
#line hidden
#nullable disable
            WriteLiteral("</h6>\r\n                                    <table class=\"table table-hover table-bordered\"");
            BeginWriteAttribute("id", " id=\"", 6629, "\"", 6637, 1);
#nullable restore
#line 129 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
WriteAttributeValue("", 6634, tb, 6634, 3, false);

#line default
#line hidden
#nullable disable
            EndWriteAttribute();
            WriteLiteral(">\r\n                                        <thead class=\"thead-dark\">\r\n                                            <tr>\r\n                                                <th>");
#nullable restore
#line 132 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                               Write(localizer.Text.col_name);

#line default
#line hidden
#nullable disable
            WriteLiteral("</th>\r\n                                                <th>");
#nullable restore
#line 133 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                               Write(localizer.Text.data_count);

#line default
#line hidden
#nullable disable
            WriteLiteral("</th>\r\n                                            </tr>\r\n                                        </thead>\r\n                                        <tbody></tbody>\r\n                                    </table>\r\n");
#nullable restore
#line 138 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                }
                                y++;
                            

#line default
#line hidden
#nullable disable
            WriteLiteral("                        </div>\r\n                        \r\n                        <label id=\"tbcount\" style=\"display:none\">");
#nullable restore
#line 143 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                            Write(Model.Count());

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n                        <label id=\"projectlist\" style=\"display:none\">");
#nullable restore
#line 144 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                                Write(ViewData["projectlist"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n                        <label id=\"pid\" style=\"display:none\">");
#nullable restore
#line 145 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                        Write(ViewData["ProjectId"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n                        <label id=\"pname\" style=\"display:none\">");
#nullable restore
#line 146 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                          Write(ViewData["ProjectName"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n                        <label id=\"pname_cht\" style=\"display:none\">");
#nullable restore
#line 147 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                              Write(ViewData["Project_Cht"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n                        <label id=\"projectlist_sec\" style=\"display:none\">");
#nullable restore
#line 148 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                                    Write(ViewData["projectlist_sec"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n                        <label id=\"projectqitable\" style=\"display:none\">");
#nullable restore
#line 149 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                                   Write(ViewData["projectqitable"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n                        <label id=\"warningtablelist\" style=\"display:none\">");
#nullable restore
#line 150 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                                                     Write(ViewData["warningtablelist"]);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</label>

                        <!--資料無誤，成功-->
                        <div class=""modal fade"" id=""lessThanThree"" tabindex=""-1"" role=""dialog"" aria-labelledby=""exampleModalCenterTitle"" aria-hidden=""true"">
                            <div class=""modal-dialog modal-dialog-centered"" role=""document"">
                                <div class=""modal-content"">
                                    <div class=""modal-header"">
                                        <h4 class=""modal-title"" id=""exampleModalLongTitle"">資料匯出</h4>
                                    </div>
                                    <div class=""modal-body"">
                                        資料匯出中，依資料大小不同需花費數分鐘到數小時不等，完成後將以狀態通知。
                                    </div>
                                    <div class=""modal-footer"">
                                        <button type=""button"" class=""btn btn_mbs"" data-dismiss=""modal"" onclick=""returntopage()"">確定</button>
                                    </div>
                ");
            WriteLiteral(@"                </div>
                            </div>
                        </div>
                        <!--資料檢查中動畫-->
                        <div class=""modal fade"" id=""datachecking"" tabindex=""-1"" role=""dialog"" aria-labelledby=""exampleModalCenterTitle"" aria-hidden=""true"">
                            <svg id=""dc-spinner"" version=""1.1"" xmlns=""http://www.w3.org/2000/svg"" x=""0px"" y=""0px""");
            BeginWriteAttribute("width:\"38", " width:\"38=\"", 9525, "\"", 9537, 0);
            EndWriteAttribute();
            BeginWriteAttribute("height:\"38", " height:\"38=\"", 9538, "\"", 9551, 0);
            EndWriteAttribute();
            WriteLiteral(@" viewBox=""-100 -20 238 238"" preserveAspectRatio=""xMinYMin meet"">
                                <text x=""14"" y=""21"" font-size=""2.5px"" style=""letter-spacing:0.2;"" fill=""grey"">
                                    資料檢查中
                                    <animate attributeName=""opacity"" values=""0;1;0"" dur=""1.8s"" repeatCount=""indefinite""></animate>
                                </text>
                                <path fill=""#cccccc"" d=""M20,35c-8.271,0-15-6.729-15-15S11.729,5,20,5s15,6.729,15,15S28.271,35,20,35z M20,5.203    C11.841,5.203,5.203,11.841,5.203,20c0,8.159,6.638,14.797,14.797,14.797S34.797,28.159,34.797,20    C34.797,11.841,28.159,5.203,20,5.203z""></path>
                                <path fill=""#cccccc"" d=""M20,33.125c-7.237,0-13.125-5.888-13.125-13.125S12.763,6.875,20,6.875S33.125,12.763,33.125,20    S27.237,33.125,20,33.125z M20,7.078C12.875,7.078,7.078,12.875,7.078,20c0,7.125,5.797,12.922,12.922,12.922    S32.922,27.125,32.922,20C32.922,12.875,27.125,7.078,20,7.078z""></path>
     ");
            WriteLiteral(@"                           <path fill=""#2AA198"" stroke=""#1890ff"" stroke-width=""0.6027"" stroke-miterlimit=""10"" d=""M5.203,20    c0-8.159,6.638-14.797,14.797-14.797V5C11.729,5,5,11.729,5,20s6.729,15,15,15v-0.203C11.841,34.797,5.203,28.159,5.203,20z"">
                                    <animatetransform attributeName=""transform"" type=""rotate"" from=""0 20 20"" to=""360 20 20"" calcMode=""spline"" keySplines=""0.4, 0, 0.2, 1"" keyTimes=""0;1"" dur=""2s"" repeatCount=""indefinite""></animatetransform>
                                </path>
                                <path fill=""#859900"" stroke=""#C2CFFE"" stroke-width=""0.5"" stroke-miterlimit=""10"" d=""M7.078,20    c0-7.125,5.797-12.922,12.922-12.922V6.875C12.763,6.875,6.875,12.763,6.875,20S12.763,33.125,20,33.125v-0.203    C12.875,32.922,7.078,27.125,7.078,20z"">
                                    <animatetransform attributeName=""transform"" type=""rotate"" from=""0 20 20"" to=""360 20 20"" dur=""1.8s"" repeatCount=""indefinite""></animatetransform>
                                <");
            WriteLiteral(@"/path>
                            </svg>
                        </div>

                        <div class=""btn btn_mbs btn_next"" onclick=""getexport()"">匯出資料</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

        <!--勾選資料大於三筆後進入資料檢查-->
    <label id=""rp_count"" style=""display: none"">");
#nullable restore
#line 194 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                          Write(ViewData["RP_Count"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"ifred\" style=\"display: none\">");
#nullable restore
#line 195 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["ifred"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_11\" style=\"display: none\">");
#nullable restore
#line 196 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_1_1"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_12\" style=\"display: none\">");
#nullable restore
#line 197 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_1_2"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_13\" style=\"display: none\">");
#nullable restore
#line 198 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_1_3"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_21\" style=\"display: none\">");
#nullable restore
#line 199 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_2_1"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_22\" style=\"display: none\">");
#nullable restore
#line 200 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_2_2"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_23\" style=\"display: none\">");
#nullable restore
#line 201 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_2_3"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_31\" style=\"display: none\">");
#nullable restore
#line 202 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_3_1"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_32\" style=\"display: none\">");
#nullable restore
#line 203 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_3_2"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"rp_33\" style=\"display: none\">");
#nullable restore
#line 204 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                       Write(ViewData["rp_tab_lst_3_3"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"riskcount\" style=\"display: none\">");
#nullable restore
#line 205 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                           Write(ViewData["riskcount"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"risklist\" style=\"display: none\">");
#nullable restore
#line 206 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                          Write(ViewData["risklist"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"dataexport\" style=\"display:none\">");
#nullable restore
#line 207 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                           Write(localizer.Message.export);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"deiderror\" style=\"display:none\">");
#nullable restore
#line 208 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                          Write(localizer.Message.deid_error);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"return_url\" style=\"display:none\">");
#nullable restore
#line 209 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                           Write(ViewData["returnurl"]);

#line default
#line hidden
#nullable disable
            WriteLiteral("</label>\r\n    <label id=\"loginname\" style=\"display: none\">");
#nullable restore
#line 210 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                           Write(ViewData["loginname"]);

#line default
#line hidden
#nullable disable
            WriteLiteral(@"</label>
</section>

<script>
    var current_value = $('#projectlist').text();
    var current_value_sec = $('#projectlist_sec').text();
    $(""#final_report"").append(current_value);
    //$(""#final_report_sec"").append(current_value_sec);
</script>
<script>
    var tbcount = $('#tbcount').text();
    var projectqitable = $('#projectqitable').text();
    var warningtablelist = $('#warningtablelist').text();
    var tbarray = new Array();
    var warnarray = new Array();
    tbarray = projectqitable.split(',');
    warnarray = warningtablelist.split(',');
    for (var i = 0; i < parseInt(tbcount); i++) {
        var tbname = '#tb_' + (i + 1).toString();
        var warnname = '#warn_' + (i + 1).toString();
        $(tbname).append(tbarray[i]);
        $(warnname).append(warnarray[i]);
    }

    var tbcount = $('#rp_count').text();
    var rp_11 = $('#rp_11').text();
    var rp_12 = $('#rp_12').text();

    var rp_21 = $('#rp_21').text();
    var rp_22 = $('#rp_22').text();

    ");
            WriteLiteral(@"var rp_31 = $('#rp_31').text();
    var rp_32 = $('#rp_32').text();

    var z = 3;
    var utility_html = ""<tr><td>{{model_name}}</td><td>{{ts}}</td><td>{{vs}}</td></tr>"";
    var utility01 = """";
    var count_nm = parseInt(tbcount);
    for (var x = 0; x < count_nm; x++) {
        //外層tab
        //alert(x);
        for (var y = 1; y < z; y++) {
            var tblenm = '#tb' + (x + 1).toString() + '_utility0' + y.toString();
            //alert('33');
            // alert(tblenm);
            //alert(y);
            //alert(rp_11);
            if (x == 0 && y == 1) {
                //     alert('44');
                utility01 = rp_11;
            } else if (x == 0 && y == 2) {
                //  alert('55');
                utility01 = rp_12;
            }
             else if (x == 1 && y == 1) {
                utility01 = rp_21;
            } else if (x == 1 && y == 2) {
                utility01 = rp_22;
            } else if (x == 2 && y == 1) {
                utility01");
            WriteLiteral(@" = rp_31;
            } else if (x == 2 && y == 2) {
                utility01 = rp_32;
            }
            //alert(utility01.list)
            $(tblenm).append(utility01);
            //alert('333');
        }

    }

    function getexport() {

       var ifred = $('#ifred').text();
       var pid = $('#pid').text();
       var pname = $('#pname').text();
       var pname_cht = $('#pname_cht').text();
       var returnurl = $('#return_url').text();
        var loginname = $('#loginname').text();

       if(ifred==""Y"")
       {
           alert('資料重新識別機率大於組織可接受之重新識別機率，無法匯出資料!');
           return;
       }
       else
       {
           //export
           exportFile();

           //location.href = """);
#nullable restore
#line 299 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                         Write(Url.Action("Step7", "ProjectStep"));

#line default
#line hidden
#nullable disable
            WriteLiteral(@"/?proj_id="" + encodeURIComponent(pid) + ""&project_name="" + encodeURIComponent(pname)+ ""&project_cht="" + encodeURIComponent(pname_cht) + ""&loginname="" + encodeURIComponent(loginname) + ""&returnurl="" + encodeURIComponent(returnurl);
       }

    }

     function exportFile() {
        $('#datachecking').modal('show');
        $('#datachecking').modal({ backdrop: 'static', keyboard: false });

     var pid = $('#pid').text();;
     var pname = $('#pname').text();
     var tbcount = $('#tbcount').text();
     var deiderror = $('#deiderror').text();
     var dataexport = $('#data_export').text();
        var returnurl = $('#return_url').text();
        var loginname = $('#loginname').text();

     $.ajax({
        type: ""get"",
        url: ""/api/WebAPI/ExportData"",
        contentType: ""application/json"",
        data:
              {
            pid: pid, p_dsname: pname
              },
        success: function (status) {
            //alert(status);
            //document.location.h");
            WriteLiteral("ref = \"");
#nullable restore
#line 326 "F:\DeIdWeb\PETS_K\DeIdWeb_V2_K\Views\ProjectStep\Step6.cshtml"
                                   Write(Url.Action("Index","Home"));

#line default
#line hidden
#nullable disable
            WriteLiteral(@""";
            if (status) {
                //exampleModalCenter
   $('#datachecking').modal('hide'); 
                $('#lessThanThree').modal({ backdrop: 'static', keyboard: false });
                $('#lessThanThree').modal('show'); 
                location.href = returnurl;
            }
            else {
                $('#datachecking').modal('hide');
                alert(deiderror);

            }
        },
        error: function (status) {
            $('#datachecking').modal('hide');
                    alert(deiderror);
            }

        });

    }
</script>

<script>
    $('.tabs').click(function(event){
        let $tab = $(event.target).parent();
        $(this).find('.active').removeClass(""active"");
        $tab.addClass('active');
        let index = $tab.index();
        $("".contents .content"").siblings('.active').removeClass('active').end().eq(index).addClass(""active"");
    })
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
        public global::Microsoft.AspNetCore.Mvc.Rendering.IHtmlHelper<IEnumerable<ProjectSampleDBData>> Html { get; private set; }
    }
}
#pragma warning restore 1591