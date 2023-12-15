using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using DeIdWeb_V2_K.Models;
using DeIdWeb_V2_K.Infrastructure.Service;
using System.Text;
using Newtonsoft.Json.Linq;
//using log4net.Core;
using Microsoft.Extensions.Logging;
using log4net;
using log4net.Repository;
using log4net.Config;
using System.IO;
using DeIdWeb_V2_K.Infrastructure.Reposiotry;
using Microsoft.Extensions.Localization;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc.Rendering;
using DeIdWeb_V2_K.Filters;
using Resources;
using Microsoft.AspNetCore.Authorization;

namespace DeIdWeb_V2_K.Controllers
{
    public class DeptController : Controller
    {
        //private readonly IStringLocalizer<HomeController> _localizer;
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();
        public Dept_Service dpService = new Dept_Service();
        public Member_Service mService = new Member_Service();
        //private readonly MySqlDBHelper _deidappsetting;
        public HttpHelper httphelp = new HttpHelper();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(DeptController));

        private readonly ILocalizer _localizer;
        public DeptController(ILocalizer localizer)
        {
            _localizer = localizer;
        }
        public IActionResult Index()
        {
            return View();
        }
        [Authorize]
        public IActionResult DeptList()
        {
            var memberlst = dpService.GetDeptList("");
            var final_memlist = "";
            if (memberlst.Count > 0)
            {
                foreach (var item in memberlst)
                {
                    var ranking_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td><a class=\"remove\" href=\"javascript:void(0)\" title=\"Remove\" onclick=\"deldept(\'{4}\')\">✖</a></td></tr>";
                    string uptime = "";
                    if (item.Updatetime.ToString("yyyy") == "0001")
                    {
                        uptime = "";
                    }
                    else
                    {
                        uptime = item.Updatetime.ToString("yyyy-MM-dd HH:mm:ss");
                    }
                    ranking_html = String.Format(ranking_html, item.Id, item.dept_name, item.Createtime, uptime, item.Id);
                    final_memlist += ranking_html;
                }
            }
            //var ranking_html = "<tr><td>{{id}}</td><td>{{name}}</td><td>{{company}}</td><td>{{email}}</td><td><a class=\"remove\" href=\"javascript:void(0)\" title=\"Remove\" onclick=\"\">✖</a></td></tr>";

            ViewData["memberlist"] = final_memlist;
            return View();
        }
    }
}