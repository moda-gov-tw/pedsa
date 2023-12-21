using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Resources;
using System.Globalization;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Mvc.Filters;

namespace DeIdWeb_V2_K.Filters
{
    public class CultureFilter : IResourceFilter
    {
        private readonly ILocalizer _localizer;

        public CultureFilter(ILocalizer localizer)
        {
            _localizer = localizer;
        }

        public void OnResourceExecuting(ResourceExecutingContext context)
        {
            var culture = context.HttpContext.Request.Path.Value.Split('/')[1];
            var hasCultureFromUrl = Regex.IsMatch(culture, @"^[A-Za-z]{2}-[A-Za-z]{2}$");
            _localizer.Culture = hasCultureFromUrl ? culture : CultureInfo.CurrentCulture.Name;
        }

        public void OnResourceExecuted(ResourceExecutedContext context)
        {
        }
    }
}
