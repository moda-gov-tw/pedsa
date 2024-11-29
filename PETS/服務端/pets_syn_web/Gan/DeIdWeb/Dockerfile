FROM mcr.microsoft.com/dotnet/core/sdk:2.1 AS dotnet-build-env

WORKDIR /app
RUN echo "#!/bin/sh\nexit 0" > /usr/sbin/policy-rc.d
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
#RUN apt-get update && apt-get install -y libgdiplus
#RUN apt-get update && apt-get install -y openssh-server
#RUN apt-get install -y fonts-wqy-microhei ttf-wqy-microhei fonts-wqy-zenhei ttf-wqy-zenhei


# 将本地的 NuGet 软件包复制到容器中
#COPY .nuget/* /app/nuget-packages/

# 在容器中安装 NuGet 软件包
#RUN nuget install /app/nuget-packages/package.nupkg -OutputDirectory /app/packages
COPY *.csproj ./
RUN dotnet restore

# 复制应用程序文件到容器中
#COPY . .

# 构建应用程序
#RUN dotnet build

COPY . ./
RUN dotnet publish -c Release -o out

ENV ASPNETCORE_URLS=http://+:11055
WORKDIR /app
EXPOSE 11055/tcp
#COPY --from=build /app/out .
#ENTRYPOINT ["dotnet", "DeIdWeb_V2.dll"]
entrypoint ["dotnet","run","--server.urls","http://localhost:11055"]
