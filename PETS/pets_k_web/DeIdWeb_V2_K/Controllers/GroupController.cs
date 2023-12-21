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
    public class GroupController : Controller
    {
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();
        public Dept_Service dpService = new Dept_Service();
        public Member_Service mService = new Member_Service();
        //private readonly MySqlDBHelper _deidappsetting;
        public HttpHelper httphelp = new HttpHelper();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(GroupController));

        private readonly ILocalizer _localizer;
        public GroupController(ILocalizer localizer)
        {
            _localizer = localizer;
        }
        public IActionResult Index()
        {
            return View();
        }
    }
}