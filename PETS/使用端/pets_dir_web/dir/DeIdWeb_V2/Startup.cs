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
using DeIdWeb_V2.Infrastructure.Reposiotry;
using DinkToPdf;
using DinkToPdf.Contracts;
using Microsoft.Extensions.FileProviders;
using System.Net;
using Microsoft.AspNetCore.Http.Features;
using System.Linq;
using DeIdWeb_V2.Infrastructure.Service;
using System.Threading.Tasks;

namespace DeIdWeb_V2
{
    public class Startup
    {
        public static ILoggerRepository repository { get; set; }
        public static IConfiguration Configuration { get; set; }
        private readonly IConfiguration config;
        public Startup(IConfiguration configuration)
        {
            //Configuration = configuration;
            this.config = configuration;

            //log4net
            repository = LogManager.CreateRepository("NETCoreRepository");
            //指定配置文件
            XmlConfigurator.Configure(repository, new FileInfo("log4net.config"));
            //var builder = new ConfigurationBuilder()
            //.SetBasePath(Directory.GetCurrentDirectory())
            //.AddJsonFile("appsettings.json");
            //Configuration = builder.Build();
        }



        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            // 注册 HttpContextAccessor
            services.AddHttpContextAccessor();
            services.AddSingleton(typeof(IConverter), new SynchronizedConverter(new PdfTools()));
            services.AddControllers();
            services.AddAntiforgery(options =>
            {
                options.HeaderName = "X-CSRF-TOKEN";
            });

            services.AddMvc()
                    .AddViewLocalization(LanguageViewLocationExpanderFormat.Suffix);//要使用View多國語系的話就加這行程式碼
            services.AddSwaggerGen(c =>
            {
                c.SwaggerDoc("v1", new OpenApiInfo { Title = "DeIdWeb API", Version = "v1" });
                c.IncludeXmlComments(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "WebAPI.xml"));
            });
            services.Configure<FormOptions>(options =>
            {
                options.ValueLengthLimit = 1024 * 1024 * 1024; // 設定1GB的上傳限制
                options.MultipartBodyLengthLimit = 1024 * 1024 * 1024; // 設定1GB的上傳限制
            });
            //Login相關
            //從組態讀取登入逾時設定
            double loginExpireMinute = this.config.GetValue<double>("LoginExpireMinute");
            // 將 Session 存在 ASP.NET Core 記憶體中
            // services.AddDistributedMemoryCache();
            services.AddSession();
            //註冊 CookieAuthentication，Scheme必填
            //驗證cookie 帳號登入方案

      
            // 省略其他配置
            services.AddControllersWithViews(options =>
            {
                //↓和CSRF資安有關，這裡就加入全域驗證範圍Filter的話，待會Controller就不必再加上[AutoValidateAntiforgeryToken]屬性
                options.Filters.Add(new AutoValidateAntiforgeryTokenAttribute());
            });
            //services.AddSingleton(Configuration);
            //var corsstr = Configuration["Cors:AllowOrigin"];
            //var corsstr = this.config["Cors:AllowOrigin"];
            //string[] corsOrigins = corsstr.Split(',', StringSplitOptions.RemoveEmptyEntries);
            services.AddCors(options =>
            {
                options.AddDefaultPolicy(builder =>
                {
                    builder.WithOrigins(
                        "https://140.96.111.164:11000",
                        "https://140.96.178.108:11000",
                        "https://140.96.111.164:5997",
                        "https://140.96.178.108:5997",
                        "https://deidweb_compose",
             
                        "http://localhost:3000", // your frontend app url
            "http://localhost:5000", // your backend app url
       
            "http://localhost:5997",
            "http://*:5000", // allow any origin
            "http://*:5997"
                    )
                    .AllowAnyMethod()
                    .AllowAnyHeader()
                    .DisallowCredentials();
                });
            });
            services.Configure<CookiePolicyOptions>(options =>
            {
                // This lambda determines whether user consent for non-essential cookies is needed for a given request.
                options.CheckConsentNeeded = context => true;
                options.MinimumSameSitePolicy = SameSiteMode.None;
            });
            services.AddScoped<ILocalizer, Localizer>();

            services.AddMvc().SetCompatibilityVersion(CompatibilityVersion.Version_3_0);
            services.AddSingleton(typeof(IConverter), new SynchronizedConverter(new PdfTools()));
            services.AddControllers();
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
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
            
            
            app.Use(async (context, next) =>
            {
                context.Response.Headers.Add("X-Frame-Options", "SAMEORIGIN");
                context.Response.Headers.Add(
                "Content-Security-Policy",
               "default-src 'self' 'unsafe-inline' ;frame-ancestors 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' 'unsafe-inline'; frame-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; font-src 'self'  'unsafe-inline' 'unsafe-eval' data:; connect-src 'self' ws:; "

                );
                await next();
            });
        
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
            app.UseStaticFiles();//加入靜態檔案
            app.UseCookiePolicy(
                new CookiePolicyOptions
                {
                    // 所有 Cookie.SamSite 設置都會被提升為 Strict
                    MinimumSameSitePolicy = SameSiteMode.Strict
                }
                );
            // app.UseStaticFiles(); //加入靜態檔案
            app.UseRouting();
            app.UseAuthentication();
            app.UseAuthorization();
          
            app.UseCors(x => x
  .WithOrigins(
      "https://140.96.111.164:11000",
      "https://140.96.178.108:11000",
      "https://140.96.111.164:5997",
      "https://140.96.178.108:5997",
      "https://deidweb_compose"
  )
  .AllowAnyMethod()
  .AllowAnyHeader()
  .DisallowCredentials()
);
            //Login相關
            //留意先執行驗證...
            
            
            //再執行Route，如此順序程式邏輯才正確

            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllerRoute(
                    name: "default",
                    pattern: "{controller=Home}/{action=StepUpload}/{id?}");

            });
        }
    }
}
