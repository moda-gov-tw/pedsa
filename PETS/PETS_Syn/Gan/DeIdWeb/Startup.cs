using System.IO;
using log4net;
using log4net.Config;
using log4net.Repository;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using System;
using System.Reflection;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Newtonsoft.Json;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc.Razor;
using System.Globalization;
using Resources;
using Microsoft.OpenApi.Models;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Http;

namespace DeIdWeb
{
    public class Startup
    {
        public static ILoggerRepository repository { get; set; }
        private readonly IConfiguration config;
        public Startup(IConfiguration configuration)
        {
            //Configuration = configuration;
            this.config = configuration;

            //log4net
            repository = LogManager.CreateRepository("NETCoreRepository");
            //指定配置文件
            XmlConfigurator.Configure(repository, new FileInfo("log4net.config"));

        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            // services.AddLocalization(options => options.ResourcesPath = "Resources");
           // services.AddSession();
            services.AddMvc()
                    .AddViewLocalization(LanguageViewLocationExpanderFormat.Suffix);//要使用View多國語系的話就加這行程式碼
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "SynWeb API", Version = "v1" });
                c.IncludeXmlComments(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "WebAPI.xml"));
            });
            //Login相關
            //從組態讀取登入逾時設定
            double loginExpireMinute = this.config.GetValue<double>("LoginExpireMinute");
            //註冊 CookieAuthentication，Scheme必填
            services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme).AddCookie(option =>
            {
                //或許要從組態檔讀取，自己斟酌決定
                option.LoginPath = new PathString("/Home/Login");//登入頁
                option.LogoutPath = new PathString("/Home/Logout");//登出Action
                                                                   //用戶頁面停留太久，登入逾期，或Controller中用戶登入時也可設定
                option.ExpireTimeSpan = TimeSpan.FromMinutes(loginExpireMinute);//沒給預設14天
            });

            services.AddScoped<ILocalizer, Localizer>();

            services.AddMvc().SetCompatibilityVersion(CompatibilityVersion.Version_2_1);
            services.AddMvc().AddJsonOptions(options =>
            {
                options.SerializerSettings.StringEscapeHandling = StringEscapeHandling.EscapeNonAscii;
            });
            
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IHostingEnvironment env)
        {
          //  app.UseSession();
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Home/Error");
            }

            var supportedCultures = new CultureInfo[] {
                new CultureInfo("en-US"),
                new CultureInfo("zh-TW")
            };
            app.UseRequestLocalization(new RequestLocalizationOptions()
            {
                SupportedCultures = supportedCultures,
                SupportedUICultures = supportedCultures,
                //當預設Provider偵測不到用戶支持上述Culture的話，就會是↓
                DefaultRequestCulture = new RequestCulture("zh-TW")//Default UICulture、Culture 
            });
            //loggerFactory.AddLog4Net();
            app.UseSwagger();
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint("/swagger/v1/swagger.json", "SynWeb API V1");
               // c.RoutePrefix = "swagger";
            });
            app.UseStaticFiles();
            app.UseCookiePolicy();
            //app.UseMvcWithDefaultRoute();
            //Login相關
            //留意先執行驗證...
            app.UseAuthentication();
            //再執行Route，如此順序程式邏輯才正確
            app.UseMvcWithDefaultRoute();
            app.UseMvc(routes =>
            {
                routes.MapRoute(
                    name: "default",
                    template: "{controller=Home}/{action=ProjectIndex}/{id?}");
            });
        }
    }
}
