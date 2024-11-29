using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using DeIdWeb_V2_K.Models;
using DeIdWeb_V2_K.Infrastructure.Service;
using log4net;
using DeIdWeb_V2_K.Infrastructure.Reposiotry;
using Microsoft.AspNetCore.Localization;
using DeIdWeb_V2_K.Filters;
using Resources;
using Microsoft.AspNetCore.Authentication;
using System.Security.Claims;
using Microsoft.Extensions.Configuration;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.Logging;
using System.Security.Principal;
using System.Linq;

namespace DeIdWeb_V2_K.Controllers
{
    [TypeFilter(typeof(CultureFilter))]
    [AutoValidateAntiforgeryToken]//
    [ResponseCache(NoStore = true)]
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger; //定義日誌物件
        //private readonly IStringLocalizer<HomeController> _localizer;
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();
        //private readonly MySqlDBHelper _deidappsetting;
        public HttpHelper httphelp = new HttpHelper();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(HomeController));
        private readonly ILocalizer _localizer;
        private readonly IConfiguration config;
        public HomeController(ILocalizer localizer, IConfiguration Config, ILogger<HomeController> logger)
        {
            _localizer = localizer;
            //_logger = logger; //初始化日誌物件
            this.config = Config;

        }

        [HttpPost]
        public IActionResult ChangeLang(string c)
        {
            string lang = CookieRequestCultureProvider.MakeCookieValue(new RequestCulture(c));
            Response.Cookies.Append(CookieRequestCultureProvider.DefaultCookieName, lang);
            return RedirectToAction("ProjectIndex", "Home");//重新導向至Index Action
        }


        public IActionResult PasswordChange()
        {
            return View();
        }

        //[Authorize]
        public IActionResult ProjectIndex()
        {
           // _logger.LogWarning("哈哈，出現錯誤拉！！"); //寫入日誌
            try
            {
                log.Info("Starting ProjectIndex");
                string selectname = _localizer.Text.select;
                //string Account = HttpContext.User.Claims.FirstOrDefault(m => m.Type == ClaimTypes.Name).Value;
                //string isAdmin = HttpContext.User.Claims.FirstOrDefault(m => m.Type == ClaimTypes.Role).Value;
                //string memberId = HttpContext.User.Claims.FirstOrDefault(m => m.Type == ClaimTypes.UserData).Value;
                string Account = "deidadmin";
                string isAdmin = "1";
                string memberId = "1";
                //TestNullLogManager();
                //HttpHelper.PostUrl("http://140.96.178.114:5900", "getDistinctData_async", "\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJhZHVsdCIsICJwcm9qSUQiOiAiMDAxIiwgInByb2pTdGVwIjogImRpc3RpbmN0IiwgImpvYk5hbWUiOiAiam9iMDMiLCAibWFpbkluZm8iOiB7ImNvbE5hbWVzIjogWyJwcmVfcmFjZSJdLCAidGFibGVOYW1lIjogImFkdWx0X3ByZTJXIiwgImRiTmFtZSI6ICJhZHVsdCIsICJyZXFGdW5jIjogMH19\"}");
                List<Member> lstMember = mydbhelper.SelectMember("select Id,UserAccount,UserName from T_Member;");
                //List<Member> lstMember = new List<Member>();
                lstMember.Insert(0, new Member { Id = 0, UserAccount = selectname });
                ViewBag.listmember = lstMember;
             
                string selectSQL = @"select TP.project_id,TP.project_name,TP.project_desc,TP.project_cht,
case when TP.updatetime is NOT null then TP.updatetime else TP.createtime end as projecttime,
tps.project_status,TM.useraccount ,case when tu.tucount > 0 then 'Y' else 'N' end as isML
from T_Project as TP
inner join T_ProjectStatus as tps on tps.project_id = TP.project_id
inner join T_Member as TM on TM.Id = TP.projectowner_id
left join(select count(*) as tucount,project_id from T_utilityResult group by project_id) as tu on TP.project_id = tu.project_id
order by TP.project_id desc; ";
                List<ProjectList> list = mydbhelper.SelectProjectList(selectSQL);
                ViewData["p_status"] = "Step2";
                foreach (var item in list)
                {
                    log.Info("Project : " + item.project_name + " ,Project_Id :" + item.project_id);
                    log.Info("ProjectStatus : "+item.project_status);
                    if (item.project_desc == "deid_testDemo")
                    {
                        if (item.project_status == 1)
                        {
                            ViewData["p_status"] = "Step4";
                        }
                        else if (item.project_status == 2)
                        {
                            ViewData["p_status"] = "Step2";
                        }
                        else if (item.project_status == 3)
                        {
                            ViewData["p_status"] = "Step3";
                        }
                        else if (item.project_status == 4)
                        {
                            ViewData["p_status"] = "Step4";
                        }
                        else if (item.project_status == 5)
                        {
                            ViewData["p_status"] = "deid_testDemo";
                        }
                    }
                }


                return View(list);
            }
            catch(Exception ex)
            {
                // _logger
                log.Error("ProjectIndex :" + ex.Message.ToString());
                return View();
            }
        }

        [AllowAnonymous]
        public IActionResult About()
        {
            return View();
        }

        public IActionResult Login()
        {

            return View();
        }

        /// <summary>
        /// 表單post提交，準備登入
        /// </summary>
        /// <param name="form"></param>
        /// <returns></returns>
        [HttpPost]
        public async Task<IActionResult> Login(string Account, string Passwd, string ReturnUrl)
        {//未登入者想進入必須登入的頁面，他會被導頁至/Home/Login，網址後面會加上QueryString:ReturnUrl(原始要求網址)

            var lstmember = mydbhelper.SelectMemberAcc(Account);
            if (lstmember.Count < 0)
            {
                //帳&密不正確
                ViewBag.errMsg = "無此帳號";
                return View();//流程不往下執行
            }

            var passwd = "";
            var isAdmin = "";
            var memId = "";
            foreach (var item in lstmember)
            {
                passwd = item.Password;
                isAdmin = item.IsAdmin.ToString();
                memId = item.Id.ToString();
                //byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(item.Password);
                //isAdmin = item.IsAdmin.ToString();
                ////參數編成 Base64 字串
                //passwd = Convert.ToBase64String(byteServer);
            }
            //轉base64
            var md5pwd = MD5Str.MD5(Passwd);
            //從自己的DB檢查帳&密，輸入是否正確
            if ((passwd == md5pwd) == false)
            {
                //帳&密不正確
                ViewBag.errMsg = "帳號或密碼輸入錯誤";
                return View();//流程不往下執行
            }

            //帳密都輸入正確，ASP.net Core要多寫三行程式碼 
            Claim[] claims = new[] { new Claim(ClaimTypes.Name, Account), new Claim(ClaimTypes.Role, isAdmin), new Claim(ClaimTypes.UserData, memId) }; //取名Account，在登入後的頁面，讀取登入者的帳號會用得到，自己先記在大腦
            //Claim[] claims = new[] { new Claim("Account", Account), new Claim("IsAdmin", isAdmin), new Claim("MemberId", memId) }; //取名Account，在登入後的頁面，讀取登入者的帳號會用得到，自己先記在大腦
            ClaimsIdentity claimsIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);//Scheme必填
            ClaimsPrincipal principal = new ClaimsPrincipal(claimsIdentity);
            //執行登入，相當於以前的FormsAuthentication.SetAuthCookie()
            //從組態讀取登入逾時設定
            double loginExpireMinute = this.config.GetValue<double>("LoginExpireMinute");
            await HttpContext.SignInAsync(principal,
                new AuthenticationProperties()
                {
                    IsPersistent = false, //IsPersistent = false，瀏覽器關閉即刻登出
                                          //用戶頁面停留太久，逾期時間，在此設定的話會覆蓋Startup.cs裡的逾期設定
                                          /* ExpiresUtc = DateTime.Now.AddMinutes(loginExpireMinute) */
                });
            //加上 Url.IsLocalUrl 防止Open Redirect漏洞
            if (!string.IsNullOrEmpty(ReturnUrl) && Url.IsLocalUrl(ReturnUrl))
            {
                //if (ReturnUrl == "/")
                //{
                    return Redirect(ReturnUrl);//導到原始要求網址
                //}
                //else
                //{
                //    return RedirectToAction("ProjectIndex", "Home");//到登入後的第一頁，自行決定
                //}
            }
            else
            {
                return RedirectToAction("ProjectIndex", "Home");//到登入後的第一頁，自行決定
            }

        }

        /// <summary>
        /// 登出
        /// </summary>
        /// <returns></returns>
        //登出 Action 記得別加上[Authorize]，不管用戶是否登入，都可以執行Logout
        public async Task<IActionResult> Logout()
        {
            await HttpContext.SignOutAsync();

            return RedirectToAction("Login", "Home");//導至登入頁
        }

        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
