<template>
      <div id="app">
        <!-- 头部导航 -->
        <header class="header">
        <el-row>
            <el-col :span="24">
              <el-menu default-active="5" class="el-menu-demo" mode="horizontal">
                <el-menu-item index="1">MySQL性能查询</el-menu-item>
              </el-menu>
            </el-col>
        </el-row>
        </header>
        <div style="position: relative;height: 60px;width: 100%;"></div>

        <main>
              <!-- 左侧导航 -->
            <div class="main-left">
              <el-menu default-active="/monitor/throughput" class="el-menu-vertical-demo" :router="true">
                <el-menu-item index="/monitor/throughput" :class="{'isActive': active}">查询吞吐量</el-menu-item>
                <el-menu-item index="/monitor/connections">连接</el-menu-item>
                <el-menu-item index="/monitor/performance">查询性能</el-menu-item>
                <el-menu-item index="/monitor/innodb" >innodb缓冲池</el-menu-item>
              </el-menu>
            </div>

              <!-- 右侧主内容区 -->
              <div  class="main-right" >
                <transition name="fade">
                  <router-view class="view"></router-view>
                </transition>
              </div>
        </main>
      </div>
    </template>

<script>
export default {}
</script>

    <style>
body {
  margin: 0;
}
#app {
  min-width: 1200px;
  margin: 0 auto;
  font-family: "Helvetica Neue", "PingFang SC", Arial, sans-serif;
}
/* 头部导航 */
header{z-index: 1000;min-width: 1200px;transition: all 0.5s ease;  border-top: solid 4px #3091F2;  background-color: #fff;  box-shadow: 0 2px 4px 0 rgba(0,0,0,.12),0 0 6px 0 rgba(0,0,0,.04);  }
header.header-fixed{position: fixed;top: 0;left: 0;right: 0;}
header .el-menu-demo{padding-left: 300px!important;}
/* 主内容区 */
main{display: -webkit-box;display: -ms-flexbox;display: flex;  min-height: 800px;  border: solid 40px #E9ECF1;  background-color: #FCFCFC;  }
main .main-left{text-align: center;-webkit-box-flex: 0;-ms-flex: 0 0 200px;flex: 0 0 200px;}
main .main-right{-webkit-box-flex:1;-ms-flex:1;flex:1; background-color: #fff; padding: 50px 70px; }
main .el-menu{background-color: transparent!important;}
/*  */
.router-link{display:inline-block;width:100%;height:100%;text-align:center;color:#475669;text-decoration: none; }
.is-active .router-link{color:#20a0ff; }
/* 单选框 */
  .el-form-item .el-radio+.el-radio {
    margin-left: 30px!important;
  }
  /* 路由切换动效 */
  .fade-enter-active, .fade-leave-active {
    transition: all .5s;
  }
  .fade-enter, .fade-leave-active {
    opacity: 0;
  }
  .list-enter-active, .list-leave-active {
    transition: all 1s;
  }
  .list-enter, .list-leave-active {
    opacity: 0;
    transform: translateY(30px);
  }
/* 导航栏菜单选中效果 */
  .isActive{color: #20a0ff!important;}
   #app main .aside .is-active{color: #475669;}
  /* 卡片 */
  .el-card{overflow: visible!important;}
</style>
