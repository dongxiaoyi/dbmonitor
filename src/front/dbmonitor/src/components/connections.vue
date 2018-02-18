<template>
<div>
  <el-form :model='form' class='demo-ruleForm'   label-position='top'>
    <el-row :gutter='20' class='address'>
      <el-col :span='1.5' style="margin-top: 5px;">
          <span class="demonstration">选择主机</span>
      </el-col>
      <el-col :span='4'>
        <el-form-item>
            <el-cascader
                :options="hostnames"
                v-model="selectedOptions"
                @change="handleChange">
            </el-cascader>
        </el-form-item>
      </el-col>
      <el-col :span='1.5' style="margin-top: 5px;">
          <span class="demonstration">选择日期</span>
      </el-col>
      <el-col :span='6'>
        <el-date-picker
                v-model="times"
                type="datetimerange"
                :picker-options="pickerOptions2"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                align="right">
        </el-date-picker>
      </el-col>
      <el-col :span='2'>
        <el-form-item>
          <el-button type="primary" @click="Queryconnections()">查询</el-button>
        </el-form-item>
      </el-col>
    </el-row>
  </el-form>
  <br>
  <el-form :model='form' :inline="true" class='demo-ruleForm'   label-position='left'>
    <el-row class='address'>
        <el-col :span='3'>
        <el-form-item label="当前主机：">
            <span>{{hostname}}   </span>
        </el-form-item>
        </el-col>
        <el-col :span='5'>
        <el-form-item label="刷新间隔：">
            <el-input v-model="intervel"></el-input>
        </el-form-item>
        </el-col>
        <el-col :span='2'>
            <el-form-item>
                <el-button type="primary" @click="AlterIntervel(hostname, intervel)">修改</el-button>
            </el-form-item>
        </el-col>
    </el-row>
  </el-form>
      <img :src="connections[0].connections" class="image" style="margin-left: 0%">
  </div>
</template>
<script>
import {connections, hostnames, queryconnections, intervel} from '../mock/api'
export default {
  data: function () {
    return {
      hostnames: [],
      connections: [],
      selectedOptions: [],
      intervel: '',
      hostname: '',
      pickerOptions2: {
        shortcuts: [{
          text: '最近一周',
          onClick (picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
            picker.$emit('pick', [start, end])
          }
        },
        {
          text: '最近一个月',
          onClick (picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
            picker.$emit('pick', [start, end])
          }
        },
        {
          text: '最近三个月',
          onClick (picker) {
            const end = new Date()
            const start = new Date()
            start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
            picker.$emit('pick', [start, end])
          }
        }]
      },
      times: ''
    }
  },
  watch: {
    form: {
      handler: function (val) {
        this.$emit('change', val)
      },
      deep: true
    }
  },
  methods: {
    handleChange (value) {
      console.log(value)
    },
    Queryconnections () {
      queryconnections({hostname_db: this.selectedOptions, times: this.times})
        .then((response) => {
          this.connections = ([response.data])
          console.log(this.connections)
        })
        .catch(function (error) {
          console.log(error)
        })
    },
    AlterIntervel () {
      intervel({hostname: this.hostname, intervel: this.intervel})
        .then((response) => {
          this.$message('修改成功！')
        })
        .catch(function (error) {
          console.log(error)
        })
    },
    handleDelete (index, row) {
      console.log(index, row)
    }
  },
  created () {
    connections()
      .then((response) => {
        console.log(response)
        this.connections = ([response.data])
        this.intervel = response.data['intervel']
        this.hostname = response.data['hostname'][0]
      })
      .catch(function (error) {
        console.log(error)
      })
    hostnames()
      .then((response) => {
        console.log(response)
        this.hostnames = (response.data)
      })
      .catch(function (error) {
        console.log(error)
      })
  }
}
</script>
<style>
.address .el-form-item {
  margin-bottom: 0 !important;
  margin-right: 0 !important
}
</style>
