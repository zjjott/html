'use strict'
const React = require('react');
const ReactDom = require('react-dom');
import {newfetch} from "./components"
import {Grid,Tab,Row,Table,Col,Radio,FormControl,FormGroup} from "react-bootstrap"
const marked = require("marked")
const _ = require("underscore")

const MethodList = React.createClass({
    contextTypes:{
        store:React.PropTypes.any
    },
    getInitialState: function() {
        this.store = this.context.store
        return {
            methods:[] 
        };
    },
    componentDidMount() {
        newfetch("/task/method/?public=true&trained=false").then(response=>{
            return response.json()
        }).then(response_json=>{
            this.setState({methods:response_json.data})
        })
        this.store.addListener("method",this.methodChange)
    },
    methodChange(){
        this.forceUpdate()
    },
    onChange(evt){
        this.store.dispatch({"type":"method",
            data:evt.target.value})
    },
    componentWillUnmount: function() {
        this.store.removeListener("method",this.methodChange)
        
    },
    render(){
        var storeState = this.store.getState()
        return <Grid>
            <Row className="show-grid">
      <Col xs={12} sm={12}>模型列表</Col>
    </Row>
        <Row className="show-grid">
      <Col xs={12} sm={12}>
        <Table condensed responsive striped>
        <thead>
            <tr>
                <th>名称</th>
                <th>描述</th>
            </tr>
        </thead>
        <tbody>{this.state.methods.map((data)=>{
            return <tr key={data.id}>
                <td>
                    <Radio onChange={this.onChange} 
                      inline 
                      name="methods"
                      checked={storeState.method==data.id}
                      value={data.id}>
                      {data.name}
                    </Radio>
                </td>
                <td dangerouslySetInnerHTML={{__html:marked(data.description)}}></td>
            </tr>
        })}
        </tbody>
        </Table>
      </Col>
    </Row>
    </Grid>

    }
})
const ArgInput = React.createClass({
    getInitialState() {
        switch(this.props.type){
            case "int":{
                return {"value":this.props.value||0}
            }
            case "list":{
                return {"value":[]}
            }
        }
    },
    handleChange(e){
        this.setState({ value: e.target.value });
    },
    addValue(){
        this.setState({value:this.state.value.concat(0)})
    },
    removeValue(index){
        return (e)=>{
            this.state.value.pop(index)
            this.setState({"value":this.state.value})
        }
    },
    render(){
        switch(this.props.type){
            case "int":
                return <FormControl
            type="number"
            value={this.state.value}
            placeholder="输入一个数字"
            onChange={this.handleChange}
          />
            case "list":
                return <FormGroup
                        >
                        <a onClick={this.addValue}>+</a>
                        {this.state.value.map((v,index)=>{
                            return [<ArgInput key={index} type="int" value={v} />,
                            <a onClick={this.removeValue(index)} className="btn btn-primary">x</a>]
                        })}
                        </FormGroup>
        }
    }
})
const MethodKwargs = React.createClass({
    getInitialState() {
        return {kwargs:[]}
    },
    contextTypes:{
        store:React.PropTypes.any
    },
    componentDidMount() {
        this.store = this.context.store
        var state = this.store.getState()
        var method_id = state.method
        newfetch(`/task/method/${method_id}/`).then(response=>{
            return response.json()
        }).then(response_json=>{
            this.setState({kwargs:response_json.data.kwargs})
        })
    },
    render(){
        return <Grid>
            <Row className="show-grid">
      <Col xs={12} sm={12}>
        <Table condensed responsive striped>
        <thead>
            <tr>
                <th>名称</th>
                <th>描述</th>
            </tr>
        </thead>
        <tbody>{this.state.kwargs.map((arg)=>{
            return <tr key={arg.id}>
                <td>
                    {arg.label}
                </td>
                <td>
                    <ArgInput type={arg.type} />
                </td>
            </tr>
        })}
        </tbody>
        </Table>
      </Col>
    </Row>
        </Grid>
    }
})
export {MethodList,MethodKwargs}