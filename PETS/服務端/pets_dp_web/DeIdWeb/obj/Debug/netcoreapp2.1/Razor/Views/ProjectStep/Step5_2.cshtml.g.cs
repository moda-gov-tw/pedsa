#pragma checksum "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml" "{ff1816ec-aa5e-4d10-87f7-6f4963833460}" "92fb6e7b34fbf057e1007f317725427dd0a1a7f1"
// <auto-generated/>
#pragma warning disable 1591
[assembly: global::Microsoft.AspNetCore.Razor.Hosting.RazorCompiledItemAttribute(typeof(AspNetCore.Views_ProjectStep_Step5_2), @"mvc.1.0.view", @"/Views/ProjectStep/Step5_2.cshtml")]
[assembly:global::Microsoft.AspNetCore.Mvc.Razor.Compilation.RazorViewAttribute(@"/Views/ProjectStep/Step5_2.cshtml", typeof(AspNetCore.Views_ProjectStep_Step5_2))]
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
#line 2 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
using System.Globalization;

#line default
#line hidden
#line 3 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
using Resources;

#line default
#line hidden
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"92fb6e7b34fbf057e1007f317725427dd0a1a7f1", @"/Views/ProjectStep/Step5_2.cshtml")]
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"e0ea9701343602d68eda9a80005fe261fbee6a2e", @"/Views/_ViewImports.cshtml")]
    public class Views_ProjectStep_Step5_2 : global::Microsoft.AspNetCore.Mvc.Razor.RazorPage<IEnumerable<ProjectSampleDBData>>
    {
        #pragma warning disable 1998
        public async override global::System.Threading.Tasks.Task ExecuteAsync()
        {
#line 5 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
  
    ViewData["Title"] = "Step5_2";
    Layout = "~/Views/Shared/_Layout.cshtml";

#line default
#line hidden
            BeginContext(208, 145, true);
            WriteLiteral("\r\n<section class=\"section_top\">\r\n    <div class=\"container\">\r\n        <ul class=\"bread_crumb\">\r\n            <li>\r\n             \r\n                ");
            EndContext();
            BeginContext(354, 68, false);
#line 15 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
           Write(Html.ActionLink(localizer.Text.project_list, "ProjectIndex", "Home"));

#line default
#line hidden
            EndContext();
            BeginContext(422, 57, true);
            WriteLiteral("\r\n            </li>\r\n            <li>\r\n                <a");
            EndContext();
            BeginWriteAttribute("href", " href=\"", 479, "\"", 604, 1);
#line 18 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
WriteAttributeValue("", 486, Url.Action("Step5_2", "ProjectStep", new { proj_id = ViewData["ProjectId"], project_name = ViewData["ProjectName"] }), 486, 118, false);

#line default
#line hidden
            EndWriteAttribute();
            BeginContext(605, 1, true);
            WriteLiteral(">");
            EndContext();
            BeginContext(607, 23, false);
#line 18 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                                                                                                            Write(ViewData["ProjectName"]);

#line default
#line hidden
            EndContext();
            BeginContext(630, 252, true);
            WriteLiteral("</a>\r\n            </li>\r\n        </ul>\r\n    </div>\r\n</section>\r\n<section class=\"project_wrapper\">\r\n   <div class=\"container\">\r\n\t<div class=\"row\">\r\n\t  <div class=\"col-sm-12\">\r\n\t\t<div class=\"col-sm-3\">\r\n\t\t\t<div class=\"status_bar\">\r\n\t\t\t\t<h4 class=\"title\">");
            EndContext();
            BeginContext(883, 23, false);
#line 29 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                             Write(ViewData["ProjectName"]);

#line default
#line hidden
            EndContext();
            BeginContext(906, 72, true);
            WriteLiteral("</h4>\r\n\t\t\t\t<div class=\"status\">\r\n\t\t\t\t\t<div class=\"status_f\">\r\n\t\t\t\t\t\t<h6>");
            EndContext();
            BeginContext(979, 20, false);
#line 32 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                       Write(localizer.Text.step1);

#line default
#line hidden
            EndContext();
            BeginContext(999, 16, true);
            WriteLiteral("</h6>\r\n\t\t\t\t\t\t<p>");
            EndContext();
            BeginContext(1016, 30, false);
#line 33 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                      Write(localizer.Text.step1_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(1046, 114, true);
            WriteLiteral("</p>\r\n\t\t\t\t\t\t<h3>1</h3>\r\n\t\t\t\t\t</div>\r\n\t\t\t\t</div>\r\n\t\t\t\t<div class=\"status\">\r\n\t\t\t\t\t<div class=\"status_d\">\r\n\t\t\t\t\t\t<h6>");
            EndContext();
            BeginContext(1161, 20, false);
#line 39 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                       Write(localizer.Text.step2);

#line default
#line hidden
            EndContext();
            BeginContext(1181, 16, true);
            WriteLiteral("</h6>\r\n\t\t\t\t\t\t<p>");
            EndContext();
            BeginContext(1198, 30, false);
#line 40 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                      Write(localizer.Text.step2_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(1228, 114, true);
            WriteLiteral("</p>\r\n\t\t\t\t\t\t<h3>2</h3>\r\n\t\t\t\t\t</div>\r\n\t\t\t\t</div>\r\n\t\t\t\t<div class=\"status\">\r\n\t\t\t\t\t<div class=\"status_d\">\r\n\t\t\t\t\t\t<h6>");
            EndContext();
            BeginContext(1343, 20, false);
#line 46 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                       Write(localizer.Text.step3);

#line default
#line hidden
            EndContext();
            BeginContext(1363, 16, true);
            WriteLiteral("</h6>\r\n\t\t\t\t\t\t<p>");
            EndContext();
            BeginContext(1380, 30, false);
#line 47 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                      Write(localizer.Text.step3_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(1410, 114, true);
            WriteLiteral("</p>\r\n\t\t\t\t\t\t<h3>3</h3>\r\n\t\t\t\t\t</div>\r\n\t\t\t\t</div>\r\n\t\t\t\t<div class=\"status\">\r\n\t\t\t\t\t<div class=\"status_d\">\r\n\t\t\t\t\t\t<h6>");
            EndContext();
            BeginContext(1525, 20, false);
#line 53 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                       Write(localizer.Text.step4);

#line default
#line hidden
            EndContext();
            BeginContext(1545, 16, true);
            WriteLiteral("</h6>\r\n\t\t\t\t\t\t<p>");
            EndContext();
            BeginContext(1562, 30, false);
#line 54 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                      Write(localizer.Text.step4_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(1592, 114, true);
            WriteLiteral("</p>\r\n\t\t\t\t\t\t<h3>4</h3>\r\n\t\t\t\t\t</div>\r\n\t\t\t\t</div>\r\n\t\t\t\t<div class=\"status\">\r\n\t\t\t\t\t<div class=\"status_d\">\r\n\t\t\t\t\t\t<h6>");
            EndContext();
            BeginContext(1707, 20, false);
#line 60 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                       Write(localizer.Text.step5);

#line default
#line hidden
            EndContext();
            BeginContext(1727, 16, true);
            WriteLiteral("</h6>\r\n\t\t\t\t\t\t<p>");
            EndContext();
            BeginContext(1744, 30, false);
#line 61 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                      Write(localizer.Text.step5_menu_list);

#line default
#line hidden
            EndContext();
            BeginContext(1774, 96, true);
            WriteLiteral("</p>\r\n\t\t\t\t\t\t<h3>5</h3>\r\n\t\t\t\t\t</div>\r\n\t\t\t\t</div>\r\n\t\t\t</div>\r\n\t\t</div>\r\n\t\t<div class=\"col-sm-9\">\r\n");
            EndContext();
            BeginContext(2152, 628, true);
            WriteLiteral(@"			<div id=""reportboard"">
                <!-- TAB CONTROLLERS-->
                <input class=""panel-radios"" id=""panel-1-ctrl"" type=""radio"" name=""tab-radios"" checked=""checked"">
                <input class=""panel-radios"" id=""panel-2-ctrl"" type=""radio"" name=""tab-radios"">
                <input class=""panel-radios"" id=""nav-ctrl"" type=""checkbox"" name=""nav-checkbox"">
                <ul id=""tabs-list"">
                  <!-- MENU TOGGLE-->
                  <label id=""open-nav-label"" for=""nav-ctrl""></label>
                  <li id=""li-for-panel-1"">
                    <label class=""panel-label"" for=""panel-1-ctrl"">");
            EndContext();
            BeginContext(2781, 27, false);
#line 84 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                             Write(localizer.Text.report_info1);

#line default
#line hidden
            EndContext();
            BeginContext(2808, 147, true);
            WriteLiteral("</label>\r\n                  </li>\r\n                  <li id=\"li-for-panel-2\">\r\n                      <label class=\"panel-label\" for=\"panel-2-ctrl\">");
            EndContext();
            BeginContext(2956, 27, false);
#line 87 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                               Write(localizer.Text.report_info2);

#line default
#line hidden
            EndContext();
            BeginContext(2983, 443, true);
            WriteLiteral(@"</label>
                  </li>
                  <label id=""close-nav-label"" for=""nav-ctrl"">×</label>
                </ul>
                <!-- THE PANELS-->
                <article id=""panels"">
                  <div class=""container"">
                    <section id=""panel-1"">
                        <main>
                            <div class=""tab-pane step05 col-sm-12"">
                                <h4 class=""title"">");
            EndContext();
            BeginContext(3427, 20, false);
#line 97 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                             Write(localizer.Text.step5);

#line default
#line hidden
            EndContext();
            BeginContext(3447, 215, true);
            WriteLiteral("</h4>\r\n                                <table class=\"table table-hover table-bordered\" id=\"final_report\">\r\n\t\t\t\t\t\t\t\t\t<!--7個欄位-->\r\n<!--\r\n\t\t\t\t\t\t\t\t\t<thead class=\"thead-dark\">\r\n\t\t\t\t\t\t\t\t\t  <tr>\r\n\t\t\t\t\t\t\t\t\t\t<th rowspan=\"2\">");
            EndContext();
            BeginContext(3663, 27, false);
#line 103 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.dataset_name);

#line default
#line hidden
            EndContext();
            BeginContext(3690, 33, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th colspan=\"2\">");
            EndContext();
            BeginContext(3724, 23, false);
#line 104 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.raw_data);

#line default
#line hidden
            EndContext();
            BeginContext(3747, 33, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th colspan=\"2\">");
            EndContext();
            BeginContext(3781, 30, false);
#line 105 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.k_checking_data);

#line default
#line hidden
            EndContext();
            BeginContext(3811, 33, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th rowspan=\"2\">");
            EndContext();
            BeginContext(3845, 27, false);
#line 106 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.data_suprate);

#line default
#line hidden
            EndContext();
            BeginContext(3872, 37, true);
            WriteLiteral(" (%)</th>\r\n\t\t\t\t\t\t\t\t\t\t<th rowspan=\"2\">");
            EndContext();
            BeginContext(3910, 25, false);
#line 107 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.min_kvalue);

#line default
#line hidden
            EndContext();
            BeginContext(3935, 56, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t  </tr>\r\n\t\t\t\t\t\t\t\t\t  <tr>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(3992, 20, false);
#line 110 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.count);

#line default
#line hidden
            EndContext();
            BeginContext(4012, 21, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(4034, 24, false);
#line 111 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.dis_count);

#line default
#line hidden
            EndContext();
            BeginContext(4058, 21, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(4080, 20, false);
#line 112 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.count);

#line default
#line hidden
            EndContext();
            BeginContext(4100, 21, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(4122, 24, false);
#line 113 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.dis_count);

#line default
#line hidden
            EndContext();
            BeginContext(4146, 139, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t  </tr>\r\n\t\t\t\t\t\t\t\t\t</thead>\r\n-->\r\n\t\t\t\t\t\t\t\t\t<!--5個欄位-->\r\n\t\t\t\t\t\t\t\t\t<thead class=\"thead-dark\">\r\n\t\t\t\t\t\t\t\t\t  <tr>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(4286, 27, false);
#line 120 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.dataset_name);

#line default
#line hidden
            EndContext();
            BeginContext(4313, 21, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(4335, 29, false);
#line 121 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.raw_data_count);

#line default
#line hidden
            EndContext();
            BeginContext(4364, 21, true);
            WriteLiteral("</th>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(4386, 27, false);
#line 122 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.data_suprate);

#line default
#line hidden
            EndContext();
            BeginContext(4413, 25, true);
            WriteLiteral(" (%)</th>\r\n\t\t\t\t\t\t\t\t\t\t<th>");
            EndContext();
            BeginContext(4439, 25, false);
#line 123 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.min_kvalue);

#line default
#line hidden
            EndContext();
            BeginContext(4464, 51, true);
            WriteLiteral("</th>\r\n                                        <th>");
            EndContext();
            BeginContext(4516, 26, false);
#line 124 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                       Write(localizer.Text.un_keycount);

#line default
#line hidden
            EndContext();
            BeginContext(4542, 294, true);
            WriteLiteral(@"</th>
									  </tr>
									</thead>
                                    <tbody></tbody>
                                </table>
                            </div>
                            <div class=""tab-pane step05 col-sm-12"">
                                <h4 class=""title"">");
            EndContext();
            BeginContext(4837, 26, false);
#line 131 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                             Write(localizer.Text.gen_setting);

#line default
#line hidden
            EndContext();
            BeginContext(4863, 7, true);
            WriteLiteral("</h4>\r\n");
            EndContext();
#line 132 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                  
                                    int x = 1;
                                    foreach (var item in Model)
                                    {
                                        string tb = "tb_" + x.ToString();

#line default
#line hidden
            BeginContext(5133, 87, true);
            WriteLiteral("                                        <table class=\"table table-hover table-bordered\"");
            EndContext();
            BeginWriteAttribute("id", " id=\"", 5220, "\"", 5228, 1);
#line 137 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
WriteAttributeValue("", 5225, tb, 5225, 3, false);

#line default
#line hidden
            EndWriteAttribute();
            BeginContext(5229, 185, true);
            WriteLiteral(">\r\n                                            <thead class=\"thead-dark\">\r\n                                                <tr>\r\n                                                    <th>");
            EndContext();
            BeginContext(5415, 26, false);
#line 140 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.ch_col_name);

#line default
#line hidden
            EndContext();
            BeginContext(5441, 63, true);
            WriteLiteral("</th>\r\n                                                    <th>");
            EndContext();
            BeginContext(5505, 26, false);
#line 141 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.en_col_name);

#line default
#line hidden
            EndContext();
            BeginContext(5531, 63, true);
            WriteLiteral("</th>\r\n                                                    <th>");
            EndContext();
            BeginContext(5595, 24, false);
#line 142 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.data_attr);

#line default
#line hidden
            EndContext();
            BeginContext(5619, 63, true);
            WriteLiteral("</th>\r\n                                                    <th>");
            EndContext();
            BeginContext(5683, 27, false);
#line 143 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.process_flow);

#line default
#line hidden
            EndContext();
            BeginContext(5710, 227, true);
            WriteLiteral("</th>\r\n                                                </tr>\r\n                                            </thead>\r\n                                            <tbody></tbody>\r\n                                        </table>\r\n");
            EndContext();
#line 148 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                        x++;
                                    }
                                

#line default
#line hidden
            BeginContext(6057, 105, true);
            WriteLiteral("                            </div>\r\n                            <label id=\"tbcount\" style=\"display:none\">");
            EndContext();
            BeginContext(6163, 13, false);
#line 152 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                                Write(Model.Count());

#line default
#line hidden
            EndContext();
            BeginContext(6176, 83, true);
            WriteLiteral("</label>\r\n                            <label id=\"projectlist\" style=\"display:none\">");
            EndContext();
            BeginContext(6260, 23, false);
#line 153 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                                    Write(ViewData["projectlist"]);

#line default
#line hidden
            EndContext();
            BeginContext(6283, 86, true);
            WriteLiteral("</label>\r\n                            <label id=\"projectqitable\" style=\"display:none\">");
            EndContext();
            BeginContext(6370, 26, false);
#line 154 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                                       Write(ViewData["projectqitable"]);

#line default
#line hidden
            EndContext();
            BeginContext(6396, 88, true);
            WriteLiteral("</label>\r\n                            <label id=\"warningtablelist\" style=\"display:none\">");
            EndContext();
            BeginContext(6485, 28, false);
#line 155 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                                         Write(ViewData["warningtablelist"]);

#line default
#line hidden
            EndContext();
            BeginContext(6513, 149, true);
            WriteLiteral("</label>\r\n                            <div class=\"btn btn_mbs btn_next\" id=\"next\" name=\"form\">\r\n                                <a class=\"a_unstyled\"");
            EndContext();
            BeginWriteAttribute("href", " href=\"", 6662, "\"", 6785, 1);
#line 157 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
WriteAttributeValue("", 6669, Url.Action("Step5", "ProjectStep", new { proj_id = ViewData["ProjectId"], project_name = ViewData["ProjectName"] }), 6669, 116, false);

#line default
#line hidden
            EndWriteAttribute();
            BeginContext(6786, 1, true);
            WriteLiteral(">");
            EndContext();
            BeginContext(6788, 19, false);
#line 157 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                                                                                                                                             Write(localizer.Text.next);

#line default
#line hidden
            EndContext();
            BeginContext(6807, 6, true);
            WriteLiteral("</a>\r\n");
            EndContext();
            BeginContext(7063, 177, true);
            WriteLiteral("                            </div>\r\n                        </main>\r\n                    </section>\r\n                    <section id=\"panel-2\">\r\n                        <main>\r\n");
            EndContext();
            BeginContext(7625, 119, true);
            WriteLiteral("                            <div class=\"tab-pane step05 col-sm-12\">\r\n                                <h4 class=\"title\">");
            EndContext();
            BeginContext(7745, 27, false);
#line 178 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                             Write(localizer.Text.warning_info);

#line default
#line hidden
            EndContext();
            BeginContext(7772, 7, true);
            WriteLiteral("</h4>\r\n");
            EndContext();
#line 179 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                  
                                    int y = 1;
                                    foreach (var item in Model)
                                    {
                                        string tb = "warn_" + y.ToString();

#line default
#line hidden
            BeginContext(8044, 87, true);
            WriteLiteral("                                        <table class=\"table table-hover table-bordered\"");
            EndContext();
            BeginWriteAttribute("id", " id=\"", 8131, "\"", 8139, 1);
#line 184 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
WriteAttributeValue("", 8136, tb, 8136, 3, false);

#line default
#line hidden
            EndWriteAttribute();
            BeginContext(8140, 185, true);
            WriteLiteral(">\r\n                                            <thead class=\"thead-dark\">\r\n                                                <tr>\r\n                                                    <th>");
            EndContext();
            BeginContext(8326, 23, false);
#line 187 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.col_name);

#line default
#line hidden
            EndContext();
            BeginContext(8349, 63, true);
            WriteLiteral("</th>\r\n                                                    <th>");
            EndContext();
            BeginContext(8413, 25, false);
#line 188 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                   Write(localizer.Text.data_count);

#line default
#line hidden
            EndContext();
            BeginContext(8438, 227, true);
            WriteLiteral("</th>\r\n                                                </tr>\r\n                                            </thead>\r\n                                            <tbody></tbody>\r\n                                        </table>\r\n");
            EndContext();
#line 193 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                    }
                                    y++;
                                

#line default
#line hidden
            BeginContext(8781, 95, true);
            WriteLiteral("                            </div>\r\n                            <a class=\"btn btn_mbs btn_next\"");
            EndContext();
            BeginWriteAttribute("href", " href=\"", 8876, "\"", 8999, 1);
#line 197 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
WriteAttributeValue("", 8883, Url.Action("Step5", "ProjectStep", new { proj_id = ViewData["ProjectId"], project_name = ViewData["ProjectName"] }), 8883, 116, false);

#line default
#line hidden
            EndWriteAttribute();
            BeginContext(9000, 1, true);
            WriteLiteral(">");
            EndContext();
            BeginContext(9002, 19, false);
#line 197 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\Step5_2.cshtml"
                                                                                                                                                                                   Write(localizer.Text.next);

#line default
#line hidden
            EndContext();
            BeginContext(9021, 6, true);
            WriteLiteral("</a>\r\n");
            EndContext();
            BeginContext(9268, 2516, true);
            WriteLiteral(@"                        </main>
                    </section>
                  </div>
                </article>
              </div>
		</div>
	</div>
  </div>
 </div>
</section>
<script>
	var current_value = $('#projectlist').text();
	$(""#final_report"").append(current_value);
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


</script>



<script>
	var risk = {};
	risk.list = [
		{risk_m: ""隨機目標再識別風險（QI-based）"", value: ""0.11%""},
		{risk_m: ""單維敏感項目再識別風險（QI-based）"", value: ""0.11");
            WriteLiteral(@"%""},
		{risk_m: ""多維敏感項目再識別風險（QI-based）"", value: ""0.11%""},
		{risk_m: ""多維敏感序列再識別風險"", value: ""0.00%""},
		{risk_m: ""單維敏感序列再識別風險"", value: ""0.00%""},
	];
	var risk_html = ""<tr><td class='half_col'>{{risk_m}}</td><td class='half_col'>{{value}}</td></tr>"";

	for (var i = 0; i < risk.list.length; i++) {
		var item_ra = risk.list[i];
		var current_risk_html =
			risk_html.replace(""{{risk_m}}"", item_ra.risk_m)
				.replace(""{{value}}"", item_ra.value)
		;
		$(""#risk"").append(current_risk_html);
	}
</script>
<script>
	var warning = {};
	warning.list = [
		{name: ""col-sm-12"", count: ""2,231""},
		{name: ""col-sm-6"", count: ""83,314,551""},
		{name: ""col-nickname"", count: ""121,209,211""},
		{name: ""address"", count: ""29,936""},
		{name: ""br_ick"", count: ""12,123""},
		{name: ""pan_qwert"", count: ""6,662""},
		{name: ""hc0215"", count: ""98,413,889""},
		{name: ""pass_w_cd"", count: ""704,183""},
		{name: ""col-md-1"", count: ""23,023""},
		{name: ""col-hc-06"", count: ""931,232""},
		{name: ""py_ca_bri"", count: ""560,136""},
");
            WriteLiteral(@"		{name: ""py_ca_diu"", count: ""27,880""},
	];
	var warning_html = ""<tr><td class='half_col'>{{name}}</td><td class='half_col text_right'>{{count}}<img src='/images/warning.png'></td></tr>"";
	
	for (var i = 0; i < warning.list.length; i++) {
		var item_ra = warning.list[i];
		var current_warning_html =
			warning_html.replace(""{{name}}"", item_ra.name)
				.replace(""{{count}}"", item_ra.count)
		;
		$(""#warning"").append(current_warning_html);
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
