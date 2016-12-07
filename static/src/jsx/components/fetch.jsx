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
export default newfetch