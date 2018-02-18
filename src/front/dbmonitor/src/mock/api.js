import axios from 'axios'

let host = 'http://localhost:8000'

export const performance = params => { return axios.get(`${host}/v1/performance/`) }
export const dbs = params => { return axios.get(`${host}/v1/performance/dbs`) }
export const hostnames = params => { return axios.get(`${host}/v1/performance/hostnames`) }
export const querydbs = params => { return axios.patch(`${host}/v1/performance/`, params) }
export const intervel = params => { return axios.patch(`${host}/v1/performance/intervel`, params) }
export const throughput = params => { return axios.get(`${host}/v1/performance/throughput/`) }
export const querythroughput = params => { return axios.patch(`${host}/v1/performance/throughput/`, params) }
export const connections = params => { return axios.get(`${host}/v1/performance/connections/`) }
export const queryconnections = params => { return axios.patch(`${host}/v1/performance/connections/`, params) }
export const innodb = params => { return axios.get(`${host}/v1/performance/innodb/`) }
export const queryinnodb = params => { return axios.patch(`${host}/v1/performance/innodb/`, params) }
