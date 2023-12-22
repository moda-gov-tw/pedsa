using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using DeIdWeb.Models;
using DeIdWeb.Infrastructure.Service;
using System.Text;
using Newtonsoft.Json.Linq;
//using log4net.Core;
using Microsoft.Extensions.Logging;
using log4net;
using log4net.Repository;
using log4net.Config;
using System.IO;
using DeIdWeb.Infrastructure.Reposiotry;
using Microsoft.Extensions.Localization;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc.Rendering;
using DeIdWeb.Filters;
using Resources;
using Microsoft.AspNetCore.Authorization;

namespace DeIdWeb.Controllers
{
    public class MemberController : Controller
    {
        //private readonly IStringLocalizer<HomeController> _localizer;
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();
        public Member_Service mService = new Member_Service();
        //private readonly MySqlDBHelper _deidappsetting;
        public HttpHelper httphelp = new HttpHelper();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(MemberController));

        private readonly ILocalizer _localizer;
        public MemberController(ILocalizer localizer)
        {
            _localizer = localizer;
        }
        public IActionResult Index()
        {
            return View();
        }
        [Authorize]
        public IActionResult MemberList()
        {
            try
            {
                string selectname = _localizer.Text.select;

                List<Dept> lstDept = mydbhelper.selectDept();
                //List<Member> lstMember = new List<Member>();
                lstDept.Insert(0, new Dept { Id = 0, dept_name = selectname });
                ViewBag.listmember = lstDept;
                var memberlst = mService.GetMemberList("");
                var final_memlist = "";
                if (memberlst.Count > 0)
                {
                    foreach (var item in memberlst)
                    {
                        var ranking_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td><a class=\"remove\" href=\"javascript:void(0)\" title=\"Remove\" onclick=\"delmember(\'{4}\')\">✖</a></td></tr>";
                        ranking_html = String.Format(ranking_html, item.Id, item.UserAccount, item.dept_name, item.Createtime, item.Id);
                        final_memlist += ranking_html;
                    }
                }
                //var ranking_html = "<tr><td>{{id}}</td><td>{{name}}</td><td>{{company}}</td><td>{{email}}</td><td><a class=\"remove\" href=\"javascript:void(0)\" title=\"Remove\" onclick=\"\">✖</a></td></tr>";

                ViewData["memberlist"] = final_memlist;
            }
            catch(Exception ex)
            {

            }
            return View();
        }

        [Authorize]
        public IActionResult MemberProfile()
        {

            return View();
        }
    }
}