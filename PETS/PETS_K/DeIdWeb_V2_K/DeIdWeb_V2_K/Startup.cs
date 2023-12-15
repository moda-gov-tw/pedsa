using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System.IO;
using log4net;
using log4net.Config;
using log4net.Repository;
using System;

using Newtonsoft.Json;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc.Razor;
using System.Globalization;
using Resources;
using Microsoft.OpenApi.Models;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Http;
using DeIdWeb_V2_K.Infrastructure.Reposiotry;

namespace DeIdWeb_V2_K
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

            /*services.AddCors(options =>
            {
                // CorsPolicy 是自訂的 Policy 名稱
                options.AddPolicy("WebAPI", policy =>
                {
                    //policy.WithOrigins("http://+ :11000", "http://+ :5098")
                    policy.AllowAnyOrigin()
                      .AllowAnyHeader()
                      .AllowAnyMethod()
                      .AllowCredentials();
                });
            });
            */

            //services.AddAntiforgery(o => o.SuppressXFrameOptionsHeader = true);
            services.AddAntiforgery(options =>
            {
                // Set Cookie properties using CookieBuilder properties†.
                options.FormFieldName = "AntiforgeryFieldname";
                options.HeaderName = "X-CSRF-TOKEN-HEADERNAME";
                options.SuppressXFrameOptionsHeader = false;
            });
            services.AddMvc()
                    .AddViewLocalization(LanguageViewLocationExpanderFormat.Suffix);//要使用View多國語系的話就加這行程式碼
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "DeIdWeb API", Version = "v1" });
                c.IncludeXmlComments(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "WebAPI.xml"));
            });
            //Login相關
            //從組態讀取登入逾時設定
            double loginExpireMinute = this.config.GetValue<double>("LoginExpireMinute");
            // 將 Session 存在 ASP.NET Core 記憶體中
           // services.AddDistributedMemoryCache();
            services.AddSession();
            //註冊 CookieAuthentication，Scheme必填
            services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme).AddCookie(option =>
            {
                //或許要從組態檔讀取，自己斟酌決定
                option.LoginPath = new PathString("/Home/Login");//登入頁
                option.LogoutPath = new PathString("/Home/Logout");//登出Action
                //用戶頁面停留太久，登入逾期，或Controller的Action裡用戶登入時，也可以設定↓
               // option.ExpireTimeSpan = TimeSpan.FromMinutes(loginExpireMinute);//沒給預設14天
                double loginTimetoMinute = loginExpireMinute * 60;
                option.Cookie.MaxAge = TimeSpan.FromSeconds(loginTimetoMinute);

                //↓資安建議false，白箱弱掃軟體會要求cookie不能延展效期，這時設false變成絕對逾期時間
                //↓如果你的客戶反應明明一直在使用系統卻容易被自動登出的話，你再設為true(然後弱掃policy請客戶略過此項檢查) 
                option.SlidingExpiration = false;
            });

            services.AddControllersWithViews(options =>
            {
                //↓和CSRF資安有關，這裡就加入全域驗證範圍Filter的話，待會Controller就不必再加上[AutoValidateAntiforgeryToken]屬性
                options.Filters.Add(new AutoValidateAntiforgeryTokenAttribute());
            });
            //services.Configure<CookiePolicyOptions>(options =>
            //{
            //    // This lambda determines whether user consent for non-essential cookies is needed for a given request.
            //    options.CheckConsentNeeded = context => true;
            //    options.MinimumSameSitePolicy = SameSiteMode.None;
            //});
            services.AddScoped<ILocalizer, Localizer>();

            services.AddMvc().SetCompatibilityVersion(CompatibilityVersion.Version_3_0);
          
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            app.Use(async (context, next) =>
            {
                context.Response.Headers.Add(
                //   "Content-Security-Policy-Report-Only",
                //"default-src https:; report-uri /endpoint;"
                "Content-Security-Policy",
                //"default-src 'self' https://localhost:11000/ ;"
                //"default-src 'self' https://localhost:11000/ ;style-src 'self' https://localhost:11000/; img-src 'self' https://localhost:11000/; frame-src 'self' https://localhost:11000/; script-src 'self' https://localhost:11000/; font-src 'self' data"
                //"default-src 'self' 'unsafe-inline';style-src 'self' 'unsafe-inline'; img-src 'self' 'unsafe-inline'; frame-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval';"
                "default-src 'self' ;style-src 'self' 'unsafe-inline'; img-src 'self' 'unsafe-inline'; frame-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; font-src 'self'  'unsafe-inline' 'unsafe-eval' data:; connect-src 'self' ws:"
                );
                await next();
            });
            //app.Use(async (context, next) =>
            //{
            //    context.Response.Headers.Add(
            //        "Content-Security-Policy",
            //        "default-src 'self';style-src 'self' 'unsafe-inline';"
            //    );
            //    await next();
            //});
            //app.UseCsp(options =>
            //{
            //    options.Styles.Allow("https:");
            //    options.Images.AllowSelf();
            //    options.Frames.Disallow();
            //    options.Scripts.AllowSelf();
            //});
            app.UseCors(x => x
              .AllowAnyMethod()
              .AllowAnyHeader()
              .SetIsOriginAllowed(origin => true) // allow any origin
              .AllowCredentials()); // allow credentials
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }
            else
            {
                app.UseExceptionHandler("/Home/Error");
                // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
                app.UseHsts();
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
            app.UseResponseCaching();
            app.UseSwagger();
            app.UseSwaggerUI(c =>
            {
                c.SwaggerEndpoint("/swagger/v1/swagger.json", "DeIdWeb API V1");
                // c.RoutePrefix = "swagger";
            });
            app.UseHttpsRedirection();
            app.UseStaticFiles();
            app.UseCookiePolicy();
            app.UseRouting();
            //Login相關
            //留意先執行驗證...
            app.UseAuthentication();
            app.UseAuthorization();
            //再執行Route，如此順序程式邏輯才正確
            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllerRoute(
                    name: "default",
                    pattern: "{controller=Home}/{action=ProjectIndex}/{id?}");
            });
        }
    }
}
