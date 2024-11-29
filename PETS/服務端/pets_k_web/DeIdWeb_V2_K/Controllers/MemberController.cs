using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using DeIdWeb_V2_K.Models;
using DeIdWeb_V2_K.Infrastructure.Service;
using log4net;
using Resources;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Http;

namespace DeIdWeb_V2_K.Controllers
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
                if(HttpContext.User.Identity.IsAuthenticated)
                {
                    string a = "";
                }
                string selectname = _localizer.Text.select;
                var selectList = new List<memberIdAdmin>()
                {
                    new memberIdAdmin {isAdmin="請選擇", value=0 },
                    new memberIdAdmin {isAdmin="是", value=1 },
                    new memberIdAdmin {isAdmin="否", value=2 }
                };

                //selectList.Where(q => q.value == 0).First(). = true;

                ViewBag.SelectList = selectList;
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
                        var ranking_html_admin = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td><a class=\"remove\" href=\"javascript:void(0)\" title=\"Remove\" onclick=\"delmember(\'{5}\')\">✖</a></td></tr>";
                        var ranking_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>";
                        var isAdmin = "";
                     
                        ranking_html = String.Format(ranking_html_admin, item.Id, item.UserAccount, item.dept_name, item.isAdminNM, item.Createtime, item.Id);
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


        //[HttpPost]
        //public ActionResult MemberList(IFormCollection foFormCollection)
        //{
        //    string a = "";
        //    return View();
        //}

        [Authorize]
        public IActionResult MemberProfile()
        {
            
            return View();
        }
    }
}