var React = require('react');
var ReactDom = require('react-dom');
import Dataset from './dataset'
import {MethodList,MethodKwargs} from './methods'
var _ = require("underscore")
import {Grid,Tab,Row,Nav,NavItem,Navbar,Panel,
    Table,Modal,
ButtonToolbar,Button} from "react-bootstrap"
import {EventStore,newfetch,GetParams} from './components'
import InputGroup from './input'
function paramsReducer(state,action){
    switch(action.type){
        case "method":{
            return _.extend(state,{method:action.data})
        } 
        case "kwargs":{
            return _.extend(state,{kwargs:action.data})

        }
        default:
            return state
    }
}
const PredictResult = React.createClass({
    render(){

        return <Table striped bordered condensed>
        {this.props.headers?<thead>
            <tr>
            {this.props.headers.map((h,index)=>{
                return <th key={index}>{h}</th>

            })
            }
            </tr>
        </thead>
        :
            <thead>
            <tr>
                <th>预测结果</th>
            </tr>
        </thead>}
        <tbody>
        {this.props.headers?
            this.props.data.map((row,index)=>{
                return <tr key={index}>
                    {this.props.headers.map((h)=>{
                        return <td key={h}>{row[h]}</td>
                    })}
                </tr>
            }):
            this.props.data.map((row,index)=>{
                return <tr key={index}>
                    <td>{row}</td>
                </tr>
            })
        }
        </tbody>
        </Table>
    }
})
const PredictProgress = React.createClass({
    childContextTypes:{
        store:React.PropTypes.any
    },
    getInitialState: function() {
        this.store = new EventStore(paramsReducer,{})
        return {
            activeTab:1,
            method:null,
            dialog:false,
            dialog_msg:"",
        };
    },
    
    getChildContext() {
        return {store: this.store};
    },
    onMethodChange(data){
        if(data!=this.state.method)
            this.setState({
                method:data
            })
    },
    componentDidMount: function() {
        this.store.addListener("method",this.onMethodChange)
    },
    componentWillUnmount: function() {
        this.store.removeListener("method",this.onMethodChange)
        
    },
    onNextStep(){
        if(this.state.activeTab<2){
            this.setState({activeTab:this.state.activeTab+1})
        }
        else{
            var state = this.store.getState()
            var form = new FormData()
            form.set("action","predict")
            form.set("sync",true)
            this.setState({
                dialog:true,
                dialog_msg:"正在努力预测中"
            })
            _.forEach(state.kwargs,(value,key)=>{
                form.set(key,value)
            })
            newfetch(`/task/method/${state.method}/`,"POST",
                {"body":form}
            ).then((response)=>{
                return response.json()
            }).then((response_json)=>{
                if(response_json.code==200){
                    this.setState({
                        dialog:true,
                        dialog_msg:<PredictResult 
                        data={response_json.data}
                        headers={response_json.headers} />
                    })
                }
                else if(response_json.code<500){
                    this.setState({dialog:true,
                        dialog_msg:"参数错误 "+_.map(response_json.error,(value,key)=>{
                            return `${key}:${value}`
                        }).join("")
                    })
                }
                else{
                    this.setState({
                        dialog:true,
                        dialog_msg:`预测失败了${response_json.code}:${response_json.error}`
                    })
                }
            })

        }
    },
    onPrevStep(){
        this.setState({activeTab:this.state.activeTab-1})
    },
    handleSelect(selectedKey) {
        this.setState({activeTab:selectedKey})
    },
    onCloseDialog(){//原则上还应该有取消请求，不然会重新蹦出来
        this.setState({"dialog":false})
    },
    render(){
        var nextBtnDisable;
        switch(this.state.activeTab)
        {
            case 1:{
                nextBtnDisable=!this.state.method
                break
            }
            case 2:{
                nextBtnDisable=false   
                break
            }
            default:
                nextBtnDisable=true
        }
        return <div>
        <Nav bsStyle="tabs" 
        justified 
        activeKey={this.state.activeTab} 
        onSelect={this.handleSelect}>
          <NavItem eventKey={1} >选择模型</NavItem>
          <NavItem eventKey={2} disabled={!this.state.method}>开始</NavItem>
        </Nav> 
        <ButtonToolbar >
        <Button className="pull-right" 
            bsStyle="primary"
            onClick={this.onNextStep}
            disabled={nextBtnDisable}>{
                this.state.activeTab<2?"下一步":"开始"
            }</Button>
        
        {this.state.activeTab>1?
            <Button className="pull-right" 
            bsStyle="primary" onClick={this.onPrevStep}>上一步</Button>
        :null}
            
        </ButtonToolbar>
        {this.state.activeTab==1?<MethodList public={true} trained={true} />:null}
        {this.state.activeTab==2?<MethodKwargs />:null}

        <Modal show={this.state.dialog} onHide={this.onCloseDialog}>
      <Modal.Header>
        <Modal.Title>预测结果</Modal.Title>
      </Modal.Header>

      <Modal.Body>
        {this.state.dialog_msg}
      </Modal.Body>

      <Modal.Footer>
        <Button onClick={this.onCloseDialog}>关闭</Button>
      </Modal.Footer>
      </Modal>
        </div> 

    }
})

export {PredictProgress}