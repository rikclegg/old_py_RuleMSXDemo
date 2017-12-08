# RuleMSXDemo.py

from EasyMSX import EasyMSX
from rulemsx import RuleMSX
from rulecondition import RuleCondition
from rule import Rule

class RuleMSXDemo:
    
    def __init__(self):

        print("Initialising RuleMSX...")
        self.ruleMSX = RuleMSX()
        print("RuleMSX initialised...")
        
        print("Create RuleSet...")
        self.buildRules()
        print("RuleSet ready...")
        
        print("Initialising EasyMSX...")
        self.easyMSX = EasyMSX()
        print("EasyMSX initialised...")
        
        self.easyMSX.orders.addNotificationHandler(self.processNotification)
        self.easyMSX.routes.addNotificationHandler(self.processNotification)

        self.easyMSX.start()
             

    def buildRules(self):
        
        condStatusNew = RuleCondition("OrderStatusIsNew", self.StringEqualityEvaluator("OrderStatus","NEW"))
        condStatusWorking = RuleCondition("OrderStatusIsWorking", self.StringEqualityEvaluator("OrderStatus","WORKING"))
        condStatusPartFilled = RuleCondition("OrderStatusIsPartFilled", self.StringEqualityEvaluator("OrderStatus","PARTFILLED"))
        condStatusFilled = RuleCondition("OrderStatusIsFilled", self.StringEqualityEvaluator("OrderStatus","FILLED"))

        condUSExchange = RuleCondition("IsUSExchange", self.StringEqualityEvaluator("Exchange","US"))
        condLNExchange = RuleCondition("IsLNExchange", self.StringEqualityEvaluator("Exchange","LN"))

        condPercentFilled = RuleCondition("Route50%Filled", self.PercentageFilledEvaluator(50))
        
        actionSetDestBrokerBB = self.ruleMSX.createAction("SetDestBroker", self.SetDestinationBroker("BB"))
        actionSetDestBrokerBMTB = self.ruleMSX.createAction("SetDestBroker", self.SetDestinationBroker("BMTB"))
        actionRouteOrder = self.ruleMSX.createAction("RouteOrder", self.RouteOrder())
        actionSendNewMessage = self.ruleMSX.createAction("SendNewMessage", self.SendMessageWithDataPointValue("New Order Created: ", "OrderNumber"))
        actionSendAckMessage = self.ruleMSX.createAction("SendAckMessage", self.SendMessageWithDataPointValue("Broker Acknowledged Route: ", "OrderNoAndRouteID"))
        actionSendFillMessage = self.ruleMSX.createAction("SendFillMessage", self.ShowFillEvent())
        actionShowOrderDetails = self.ruleMSX.createAction("ShowOrderDetails", self.ShowOrderDetails())
        actionShowRouteDetails = self.ruleMSX.createAction("ShowRouteDetails", self.ShowRouteDetails())
        actionCancelRoute = self.ruleMSX.createAction("CancelRoute", self.CancelRoute())
        
        demoRuleSet = self.ruleMSX.createRuleSet("demoRuleSet")

        ruleNewOrder = demoRuleSet.addRule("NewOrder")
        ruleNewOrder.addRuleCondition(condStatusNew)
        
        ruleWorkingOrder = demoRuleSet.addRule("WorkingOrder")
        ruleWorkingOrder.addRuleCondition(condStatusWorking)

        rulePartFilledOrder = demoRuleSet.addRule("PartFilledOrder")
        rulePartFilledOrder.addRuleCondition(condStatusPartFilled)

        ruleFilledOrder = demoRuleSet.addRule("FilledOrder")
        ruleFilledOrder.addRuleCondition(condStatusFilled)

        ruleSetUSDestBroker = demoRuleSet.addRule("SetUSDestBroker")
        ruleSetUSDestBroker.addRuleCondition(condUSExchange)
        
        ruleRouteOrder = demoRuleSet.addRule("RouteOrder")
        

    def processNotification(self,notification):

        if notification.category == EasyMSX.NotificationCategory.ORDER:
            print("\nChange to Order (" + EasyMSX.NotificationType.asText(notification.type) + "): " + notification.source.field("EMSX_SEQUENCE").value())
            #self.printFieldChanges(notification.fieldChanges)
            #self.printOrderBlotter()

        elif notification.category == EasyMSX.NotificationCategory.ROUTE:
            print("\nChange to Route (" + EasyMSX.NotificationType.asText(notification.type) + "): " + notification.source.field("EMSX_SEQUENCE").value() + "/" + notification.source.field("EMSX_ROUTE_ID").value())
            #printFieldChanges(notification.fieldChanges)
            #printRouteBlotter()
            
        notification.consume=True


if __name__ == '__main__':
    
    ruleMSXDemo = RuleMSXDemo();
    
    input("Press any to terminate")

    print("Terminating...")

    quit()
    