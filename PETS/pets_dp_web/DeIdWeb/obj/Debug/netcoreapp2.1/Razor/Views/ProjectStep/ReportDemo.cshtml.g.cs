#pragma checksum "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\ReportDemo.cshtml" "{ff1816ec-aa5e-4d10-87f7-6f4963833460}" "6ac14e3479f6c76785d3071254251ae454b8a492"
// <auto-generated/>
#pragma warning disable 1591
[assembly: global::Microsoft.AspNetCore.Razor.Hosting.RazorCompiledItemAttribute(typeof(AspNetCore.Views_ProjectStep_ReportDemo), @"mvc.1.0.view", @"/Views/ProjectStep/ReportDemo.cshtml")]
[assembly:global::Microsoft.AspNetCore.Mvc.Razor.Compilation.RazorViewAttribute(@"/Views/ProjectStep/ReportDemo.cshtml", typeof(AspNetCore.Views_ProjectStep_ReportDemo))]
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
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"6ac14e3479f6c76785d3071254251ae454b8a492", @"/Views/ProjectStep/ReportDemo.cshtml")]
    [global::Microsoft.AspNetCore.Razor.Hosting.RazorSourceChecksumAttribute(@"SHA1", @"e0ea9701343602d68eda9a80005fe261fbee6a2e", @"/Views/_ViewImports.cshtml")]
    public class Views_ProjectStep_ReportDemo : global::Microsoft.AspNetCore.Mvc.Razor.RazorPage<dynamic>
    {
        #pragma warning disable 1998
        public async override global::System.Threading.Tasks.Task ExecuteAsync()
        {
            BeginContext(0, 2, true);
            WriteLiteral("\r\n");
            EndContext();
#line 2 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\ReportDemo.cshtml"
  
    ViewData["Title"] = "ReportDemo";
    Layout = "~/Views/Shared/_Layout.cshtml";

#line default
#line hidden
            BeginContext(95, 472, true);
            WriteLiteral(@"
<script>
    var modal = document.getElementById('myModal');
    var btn = document.getElementById(""login"");
    var span = document.getElementsByClassName(""close"")[0];
    btn.onclick = function() {
        modal.style.display = ""block"";
    }
    span.onclick = function() {
        modal.style.display = ""none"";
    }
</script>
<section class=""section_top"">
    <div class=""container"">
        <ul class=""bread_crumb"">
            <li>
                ");
            EndContext();
            BeginContext(568, 45, false);
#line 22 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\ReportDemo.cshtml"
           Write(Html.ActionLink("首頁", "ProjectIndex", "Home"));

#line default
#line hidden
            EndContext();
            BeginContext(613, 2, true);
            WriteLiteral("\r\n");
            EndContext();
            BeginContext(675, 37, true);
            WriteLiteral("            </li>\r\n            <li>\r\n");
            EndContext();
            BeginContext(774, 16, true);
            WriteLiteral("                ");
            EndContext();
            BeginContext(791, 47, false);
#line 27 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\ReportDemo.cshtml"
           Write(Html.ActionLink("議題列表", "ProjectIndex", "Home"));

#line default
#line hidden
            EndContext();
            BeginContext(838, 55, true);
            WriteLiteral("\r\n            </li>\r\n            <li>\r\n                ");
            EndContext();
            BeginContext(894, 50, false);
#line 30 "F:\DeIdWeb\數位部\pets_dp\DeIdWeb\Views\ProjectStep\ReportDemo.cshtml"
           Write(Html.ActionLink("報表", "ReportDemo", "ProjectStep"));

#line default
#line hidden
            EndContext();
            BeginContext(944, 5101, true);
            WriteLiteral(@"
            </li>
        </ul>
    </div>
</section>
<section class=""inside report"">
    <div class=""container"">
        <h4 class=""title"">報表</h4>
        <button class=""btn btn_mbs"" id=""print"">匯出報表</button>
        <div class=""col-sm-12"">
            <h5 class=""title"">資料去識別化處理結果</h5>
            <table class=""table table-bordered"" id=""final_report"">
                <thead>
                    <tr>
                        <th>資料集名稱</th>
                        <th>原始資料筆數</th>
                        <th>資料壓抑率(%)</th>
                        <th>最小等價類大小</th>
                        <th>資料個體數</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
            <table class=""table table-bordered"" id=""r1r2"">
                <thead>
                    <tr>
                        <th>組織可接受重新識別機率（R1）</th>
                        <th>資料重新識別機率（R2）</th>
                    </tr>
                </thead>
                <tbody>
      ");
            WriteLiteral(@"              <tr>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class=""col-sm-12"">
            <h5 class=""title"">概化規則設定</h5>
            <h6>表格：adult</h6>
            <table class=""table table-hover table-bordered"" id=""de_id_setting_report"">
                <thead>
                    <tr>
                        <th>中文欄位名稱</th>
                        <th>英文欄位名稱</th>
                        <th>資料隱私設定</th>
                        <th>處理過程</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
</section>
<script>
    var final_report = {};

    final_report.list = [{
        name: ""adult"",
        data_num: ""32294"",
        sup_rate: ""0.82"",
        little: ""5"",
        id_num: ""32,561""
    }];
    var ranking_html = ""<tr><td>{{name}}</td><td>{{data_num}}</td><td>{{sup_rate}}<");
            WriteLiteral(@"/td><td>{{little}}</td><td>{{id_num}}</td></tr>"";
    //var ranking_html＿test = ""<tr><td>104損益表</td><td>782,184</td><td>{{sup_rate}}</td><td>{{little}}</td><td>{{id_num}}</td></tr>"";

    var current_ranking_html = """";
    //alert('Length :' + final_report.list.length);
    for (var i = 0; i < final_report.list.length; i++) {
        var item_ra = final_report.list[i];
        current_ranking_html += ""<tr><td>"" + item_ra.name + ""</td><td>"" + item_ra.data_num + ""</td><td>"" + item_ra.sup_rate + ""</td><td>"" + item_ra.little + ""</td><td>"" + item_ra.id_num + ""</td></tr>""
            //current_ranking_html =
            //  ranking_html.replace(""{{name}}"", item_ra.name)
            // .replace(""{{data_num}}"", item_ra.data_num)
            //.replace(""{{sup_rate}}"", item_ra.sup_rate)
            //.replace(""{{little}}"", item_ra.little)
            //.replace(""{{id_num}}"", item_ra.id_num);

    }
    //alert('HTML :' + current_ranking_html);
    $(""#final_report"").append(current_ranking_html);
    /");
            WriteLiteral(@"/document.getElementById('#final_report').append(current_ranking_html);
</script>
<script>
    var setting_report1 = {};
    setting_report1.list = [{
        c_field: ""age"",
        e_field: ""age"",
        data_attr: ""間接識別"",
        process: ""十歲區間""
    }, {
            c_field: ""race"",
        e_field: ""race"",
        data_attr: ""間接識別"",
        process: ""不處理""
    }, {
            c_field: ""sex"",
        e_field: ""sex"",
        data_attr: ""間接識別"",
        process: ""不處理""
        }
        , {
            c_field: ""marital_status"",
            e_field: ""marital_status"",
            data_attr: ""間接識別"",
            process: ""自定義""
        }
        ,
        {
            c_field: ""capital_gain"",
            e_field: ""capital_gain"",
            data_attr: ""敏感資料"",
            process: ""50區間""
        },
        {
            c_field: ""capital_loss"",
            e_field: ""capital_loss"",
            data_attr: ""敏感資料"",
            process: ""100區間""
        },
        {
            c");
            WriteLiteral(@"_field: ""hours_per_week"",
            e_field: ""hours_per_week"",
            data_attr: ""敏感資料"",
            process: ""自定義""
        }];
    var setting_report1_html = ""<tr><td>{{c_field}}</td><td>{{e_field}}</td><td>{{data_attr}}</td><td>{{process}}</td></tr>"";
    var current_setting_report1_html = """";


    for (var i = 0; i < setting_report1.list.length; i++) {
        var item_sa = setting_report1.list[i];
        current_setting_report1_html += ""<tr><td>"" + item_sa.c_field + ""</td><td>"" + item_sa.e_field + ""</td><td>"" + item_sa.data_attr + ""</td><td>"" + item_sa.process + ""</td></tr>"";
        //      var current_setting_report1_html =
        //        setting_report1_html.replace(""{{c_field}}"", item_sa.c_field)
        //      .replace(""{{e_field}}"", item_sa.e_field)
        //    .replace(""{{data_attr}}"", item_sa.data_attr)
        //  .replace(""{{process}}"", item_sa.process);
    }

    $(""#de_id_setting_report"").append(current_setting_report1_html);
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