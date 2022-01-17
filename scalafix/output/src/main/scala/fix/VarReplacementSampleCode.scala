package fix

import io.cloudknox.models.common.BaseContext
import io.cloudknox.models.common.BaseContext._
import scala.Int
import scala.Boolean

trait VarReplacementSampleCode {
  def fun0a(implicit context: BaseContext)
  def fun0(implicit context: BaseContext)
  def fun0(i: Int)(implicit context: BaseContext)
  def fun0()(implicit c: Int, b: Int, context: BaseContext)
  def fun0(implicit c: Int, b: Int, context: BaseContext)

  def fun1a(implicit context: BaseContext): Unit
  def fun1(implicit context: BaseContext): Unit
  def fun1(i: Int)(implicit context: BaseContext): Unit
  def fun1b(i: Int)(implicit context: BaseContext): Unit
  def fun1()(implicit c: Int, b: Int, context: BaseContext): Unit
  def fun1(implicit c: Int, b: Int, context: BaseContext): Unit

  def fun2(implicit context: BaseContext) = {val b = (); s"s"}
  def fun2b(implicit context: BaseContext) = {val b = (); s"s"}
  def fun2c(implicit context: BaseContext): Unit = {()}
  def fun2(i: Int)(implicit context: BaseContext): Unit = {()}
  def fun2b(i: Int)(implicit context: BaseContext): Unit = {()}
  def fun2(i: Int)(a: Int)(f: Int => Int)(implicit b: Int, context: BaseContext): Unit = {()}
  def fun211(i: Int, j: Int)(a: Int)(f: Int => Int)(implicit bi: Int, context: BaseContext): Unit = {()}
  def fun211(i: Int)(a: Int)(f: Int => Int)(implicit bi: Int, context: BaseContext) = {()}
}