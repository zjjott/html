const fetch = require("isomorphic-fetch")
const _ = require("underscore")

function newfetch(url,method="GET",options){
    var default_options = {
        credentials: 'include',
        method:method,
        headers:{
            "X-AJAX":1,
        }
    }
    default_options = _.extend(default_options,options)
    return fetch(url,default_options)

}
class GetParams{
    constructor(options){
        this.o = options||{}
    }
    toString(){
        var params=[]
        for(var key in this.o){
            params.push(`${key}=${this.o[key]}`)

        }
        return params.join("&")
    }
    set(key,value){
        this.o[key]=value
    }
}
export {newfetch,GetParams}