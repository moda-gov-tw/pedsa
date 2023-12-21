using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Resources;

// For more information on enabling MVC for empty projects, visit https://go.microsoft.com/fwlink/?LinkID=397860

namespace DeIdWeb_V2.Controllers
{
    public class BaseController : Controller
    {
        private readonly ILocalizer _localizer;
        private readonly ILogger<HomeController> _logger; //定義日誌物件
        private readonly IConfiguration config;
        
        protected new void OnActionExecuting(ActionExecutingContext filterContext)
        {
            base.OnActionExecuting(filterContext);

            // 檢查使用者是否已經通過驗證
            if (!User.Identity.IsAuthenticated)
            {
                // 如果使用者沒有通過驗證，可以執行一些操作，例如重新導向到登錄頁面
                filterContext.Result = RedirectToAction("ReturnToTaipei", "Home");
            }
        }
    }
}

